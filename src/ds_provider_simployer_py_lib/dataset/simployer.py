"""
**File:** ``simployer.py``
**Region:** ``ds_provider_simployer_py_lib/dataset/simployer.py``

Simployer Dataset

This module implements a dataset for Simployer APIs.

Example:
    >>> from uuid import uuid4
    >>> dataset = SimployerDataset(
    ...     id=uuid4(),
    ...     name="employees_dataset",
    ...     version="1.0.0",
    ...     settings=SimployerDatasetSettings(
    ...         data_product=SimployerDataProducts.EMPLOYEES,
    ...         read=ReadSettings(page_size=100),
    ...     ),
    ...     linked_service=SimployerLinkedService(
    ...         id=uuid4(),
    ...         name="simployer_connection",
    ...         version="1.0.0",
    ...         settings=SimployerLinkedServiceSettings(
    ...             client_id="your_client_id",
    ...             client_secret="your_client_secret",
    ...         ),
    ...     ),
    ... )
    >>> linked_service = dataset.linked_service
    >>> linked_service.connect()
    >>> dataset.read()
    >>> data = dataset.output
"""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import pandas as pd
from ds_common_logger_py_lib import Logger
from ds_common_serde_py_lib import Serializable
from ds_resource_plugin_py_lib.common.resource.dataset import DatasetSettings, DatasetStorageFormatType, TabularDataset
from ds_resource_plugin_py_lib.common.resource.dataset.errors import (
    ReadError,
)
from ds_resource_plugin_py_lib.common.resource.errors import NotSupportedError
from ds_resource_plugin_py_lib.common.serde.deserialize import PandasDeserializer
from ds_resource_plugin_py_lib.common.serde.serialize import PandasSerializer

from ..enums import ResourceType, SimployerDataProducts, get_endpoint_for_product
from ..linked_service.simployer import SimployerLinkedService

logger = Logger.get_logger(__name__, package=True)


@dataclass(kw_only=True)
class ReadSettings(Serializable):
    """Settings specific to the read() operation.

    These settings only apply when reading data from the API
    and do not affect create(), update() or delete() operations

    """

    page: int = 1
    """Page number for pagination. Default is 1."""

    page_size: int = 100
    """Number of records per page for pagination. Default is 100."""

    from_date: str | None = None
    """Start date for filtering data, in YYYY-MM-DD format. Optional."""

    to_date: str | None = None
    """End date for filtering data, in YYYY-MM-DD format. Optional."""

    filters: dict[str, Any] | None = None
    """Additional filters for the API request. Optional."""


@dataclass(kw_only=True)
class SimployerDatasetSettings(DatasetSettings):
    data_product: SimployerDataProducts
    """Data product associated with this dataset (e.g., "employees").

    Used to determine the API endpoint and other settings.
    """

    read: ReadSettings = field(default_factory=ReadSettings)
    """Settings for read()."""


SimployerDatasetSettingsType = TypeVar(
    "SimployerDatasetSettingsType",
    bound=SimployerDatasetSettings,
)
SimployerLinkedServiceType = TypeVar(
    "SimployerLinkedServiceType",
    bound=SimployerLinkedService[Any],
)


@dataclass(kw_only=True)
class SimployerDataset(
    TabularDataset[SimployerLinkedServiceType, SimployerDatasetSettingsType, PandasSerializer, PandasDeserializer],
    Generic[SimployerLinkedServiceType, SimployerDatasetSettingsType],
):
    linked_service: SimployerLinkedServiceType
    settings: SimployerDatasetSettingsType

    serializer: PandasSerializer | None = field(
        default_factory=lambda: PandasSerializer(format=DatasetStorageFormatType.JSON),
    )
    deserializer: PandasDeserializer | None = field(
        default_factory=lambda: PandasDeserializer(format=DatasetStorageFormatType.JSON),
    )

    @property
    def type(self) -> ResourceType:
        return ResourceType.SIMPLOYER_DATASET

    @property
    def supports_checkpoint(self) -> bool:
        """
        Whether this provider supports incremental loads via ``self.checkpoint``.

        This implementation uses a simple dictionary-based checkpoint structure to
        support resuming paginated reads:

        - On a full load, ``self.checkpoint`` is expected to be empty (``{}``) or
          ``None``. In this case, :meth:`read` starts from page ``1``.
        - After each successfully read page, :meth:`read` sets
          ``self.checkpoint = {"last_page": page}``, where ``page`` is the last
          completed page number.
        - On a subsequent run, if ``self.checkpoint`` contains a ``"last_page"``
          entry, :meth:`read` resumes from ``last_page + 1`` and continues
          fetching data from the Simployer API.

        This allows consumers to perform incremental loads by persisting and
        reusing the checkpoint between executions, avoiding re-reading pages that
        were already processed successfully.

        Returns:
             bool: True if checkpointing is supported, False otherwise.
        """
        return True

    def read(self) -> None:
        """
        Read data from the requested endpoint of the Simployer API.

        Raises:
            ReadError: If reading data fails.
        """
        logger.info("Reading data from Simployer API for product: %s", self.settings.data_product)
        session = self.linked_service.connection

        # Determine starting page: resume from checkpoint or start fresh
        page = self.checkpoint.get("last_page", 0) + 1 if self.checkpoint else self.settings.read.page
        logger.info("%s load from page %s", "Resuming incremental" if self.checkpoint else "Starting full load", page)

        all_records: list[dict[str, Any]] = []
        last_successful_page = page - 1  # Track last completed page

        try:
            while True:
                params = self._build_params(page)
                response = session.request(method="GET", url=self._build_url(), params=params)
                resp_json = response.json()

                all_records.extend(resp_json.get("records", []))
                last_successful_page = page

                if not resp_json.get("has_next_page", False):
                    break
                page += 1

        except Exception as exc:
            logger.error("Failed to read resource: %s", exc)
            raise ReadError(
                message=f"Failed to read data from Simployer API for product {self.settings.data_product} at page {page}",
                details={
                    "last_successful_page": last_successful_page,
                    "failed_page": page,
                    "data_product": self.settings.data_product,
                    "settings": self.settings.read.serialize(),
                },
            ) from exc

        finally:
            self.output = pd.DataFrame(all_records)
            if not self.output.empty:
                self._set_schema(self.output)
            self.checkpoint = self._build_checkpoint(last_successful_page)

    def create(self) -> None:
        raise NotSupportedError("Method (create) not supported by Simployer provider.")

    def delete(self) -> None:
        raise NotSupportedError("Method (delete) not supported by Simployer provider.")

    def rename(self) -> None:
        raise NotSupportedError("Method (rename) not supported by Simployer provider.")

    def list(self) -> None:
        raise NotSupportedError("Method (list) not supported by Simployer provider.")

    def close(self) -> None:
        """Release any resources held by the dataset.

        For Simployer, the dataset holds no resources directly.
        Connection lifecycle is managed by the linked service.
        """

    def update(self) -> None:
        raise NotSupportedError("Method (update) not supported by Simployer provider.")

    def upsert(self) -> None:
        raise NotSupportedError("Method (upsert) not supported by Simployer provider.")

    def purge(self) -> None:
        raise NotSupportedError("Method (purge) not supported by Simployer provider.")

    def _set_schema(self, content: pd.DataFrame) -> None:
        """Set the schema from the DataFrame content."""
        self.schema = {
            str(col): str(dtype) for col, dtype in content.convert_dtypes(dtype_backend="pyarrow").dtypes.to_dict().items()
        }

    def _build_params(self, page: int) -> dict[str, Any]:
        """Build query parameters for the API request."""
        params: dict[str, Any] = {"page": page, "pageSize": self.settings.read.page_size}
        if self.settings.read.from_date:
            params["fromDate"] = self.settings.read.from_date
        if self.settings.read.to_date:
            params["toDate"] = self.settings.read.to_date
        if self.settings.read.filters:
            params.update(self.settings.read.filters)
        return params

    def _build_checkpoint(self, last_page: int) -> dict[str, Any]:
        """Build checkpoint dictionary for incremental load support."""
        return {
            "last_page": last_page,
            "page_size": self.settings.read.page_size,
            "from_date": self.settings.read.from_date,
            "to_date": self.settings.read.to_date,
            "data_product": self.settings.data_product.value,
        }

    def _build_url(self) -> str:
        """
        Helper to build the full API URL with optional path parameters.
        """

        base_endpoint = get_endpoint_for_product(self.settings.data_product)
        if base_endpoint is None:
            raise ValueError(
                f"Cannot build URL: data_product '{self.settings.data_product.value}' is not supported or not yet mapped."
            )

        host = self.linked_service.settings.host.rstrip("/")
        return f"{host}{base_endpoint}"
