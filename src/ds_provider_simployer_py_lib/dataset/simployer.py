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

import re
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import pandas as pd
from ds_common_logger_py_lib import Logger
from ds_common_serde_py_lib import Serializable
from ds_resource_plugin_py_lib.common.resource.dataset import DatasetSettings, DatasetStorageFormatType, TabularDataset
from ds_resource_plugin_py_lib.common.resource.dataset.errors import (
    CreateError,
    ReadError,
)
from ds_resource_plugin_py_lib.common.resource.errors import NotSupportedError
from ds_resource_plugin_py_lib.common.serde.deserialize import PandasDeserializer
from ds_resource_plugin_py_lib.common.serde.serialize import PandasSerializer

from ..endpoint_info import EndpointInfo
from ..enums import ResourceType, SimployerDataProducts
from ..linked_service.simployer import SimployerLinkedService

logger = Logger.get_logger(__name__, package=True)


@dataclass(kw_only=True)
class ReadSettings(Serializable):
    """Settings specific to the read() operation.

    These settings only apply when reading data from the API
    and do not affect create(), update() or delete() operations

    When set, pagination settings are ignored and a single GET request is made
    to the resource-specific endpoint (e.g., /v1/persons/{id}).
    Note: Not all endpoints support single-record lookup (e.g., /v1/employees).
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
    data_product: SimployerDataProducts | None = None
    """Data product associated with this dataset (e.g., "employees").

    Used to determine the API endpoint and other settings.
    """

    resource_id: str | None = None
    """For read operations, if set, indicates a single resource lookup by ID (e.g., /v1/persons/{id}).
    If None, read() performs based on read settings (pagination, filters, etc.) on the collection endpoint (e.g., /v1/employees).
    Note: Not all data products support single-record lookup.

    For create operations, this is mandatory and indicates the ID of the resource to create (e.g., /v1/persons/{id}).
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

        # Ensure data_product is not None
        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")

        # Single resource lookup by ID
        if self.settings.resource_id:
            self._read_single_resource(session)
            return

        # Collection read with pagination
        self._read_collection(session)

    def _read_single_resource(self, session: Any) -> None:
        """Fetch a single resource by ID."""
        resource_id = self.settings.resource_id
        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")
        url = f"{self._build_url(self.settings.data_product)}/{resource_id}"
        logger.info("Fetching single resource: %s", url)

        try:
            response = session.get(url=url)
            record = response.json()
            self.output = pd.DataFrame([record] if isinstance(record, dict) else record)
        except Exception as exc:
            logger.error("Failed to read single resource: %s", exc)
            raise ReadError(
                message=f"Failed to read {self.settings.data_product} with ID {resource_id}",
                details={
                    "resource_id": resource_id,
                    "data_product": self.settings.data_product,
                },
            ) from exc

    def _read_collection(self, session: Any) -> None:
        """Fetch collection with pagination."""
        # Determine starting page: resume from checkpoint or start fresh
        page = self.checkpoint.get("last_page", 0) + 1 if self.checkpoint else self.settings.read.page
        logger.info("%s load from page %s", "Resuming incremental" if self.checkpoint else "Starting full", page)

        all_records: list[dict[str, Any]] = []
        last_successful_page = page - 1  # Track last completed page

        try:
            if self.settings.data_product is None:
                raise NotSupportedError("Data product must be specified.")
            if not EndpointInfo.supports_method(self.settings.data_product, "GET"):
                raise NotSupportedError(f"Read (GET) not supported for data product '{self.settings.data_product.value}'.")
            while True:
                params = self._build_params(page)
                url = self._build_url(self.settings.data_product)
                response = session.get(url=url, params=params)
                records = response.json()

                if isinstance(records, list):
                    all_records.extend(records)
                elif records is not None:
                    all_records.extend([records])
                last_successful_page = page

                # Pagination info is in response headers (x-has-next-page)
                has_next = response.headers.get("x-has-next-page", "false").lower() == "true"
                if not has_next:
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
            # Always set output as a DataFrame, even if all_records is empty
            self.output = pd.DataFrame(all_records)
            self.checkpoint = self._build_checkpoint(last_successful_page)

    def create(self) -> None:
        """
        Insert rows into Simployer API.

        Reads from self.input (which must be a pandas DataFrame) and POSTs to the configured endpoint.
        Results are stored in self.output.

        Input Requirement:
            - self.input must be a pandas DataFrame with columns matching the Simployer endpoint schema.
            - Only one record per create() call is allowed (one row in the DataFrame).
            - Users must convert their data (dict, JSON, etc.) to a DataFrame before assigning to self.input.

        Example:
            import pandas as pd
            data = {
                "firstName": "John",
                "lastName": "Doe",
                "primaryEmail": "john.doe@example.com",
                "affiliatedOrganizationId": "org-12345"
            }
            dataset.input = pd.DataFrame([data])
            dataset.create()

        The caller can also provide raw data and use the deserializer to convert:
            dataset.input = dataset.deserializer.deserialize(raw_bytes)
            dataset.create()

        Raises:
            NotSupportedError: If the configured data product does not support create (POST).
            CreateError: If creating records fails.
        """
        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")
        if EndpointInfo.supports_method(self.settings.data_product, "POST") is False:
            raise NotSupportedError(f"Create (POST) not supported for data product '{self.settings.data_product.value}'.")

        if self.input is None or self.input.empty:
            logger.info("No input data to create, returning empty output")
            self.output = pd.DataFrame()
            return

        # Capacity limit: Simployer accepts 1 record per POST for atomicity
        if len(self.input) > 1:
            raise CreateError(
                message="Simployer API accepts 1 record per request. Caller must batch.",
                details={"input_rows": len(self.input), "capacity": 1},
            )

        # Don't mutate self.input - work on copy
        row = self.input.iloc[0].to_dict()

        session = self.linked_service.connection

        # Use data_product from settings
        url = self._build_url(self.settings.data_product)
        logger.info("Creating record at %s", url)

        try:
            response = session.post(url=url, json=row)
            result = response.json()

            # Populate self.output with backend response
            self.output = pd.DataFrame([result] if isinstance(result, dict) else result)
        except Exception as exc:
            logger.error("Failed to create record: %s", exc)
            raise CreateError(
                message=f"Failed to create {self.settings.data_product.value}",
                details={"data_product": self.settings.data_product.value},
            ) from exc

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
        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")
        return {
            "last_page": last_page,
            "page_size": self.settings.read.page_size,
            "from_date": self.settings.read.from_date,
            "to_date": self.settings.read.to_date,
            "data_product": self.settings.data_product.value,
        }

    def _build_url(self, data_product: SimployerDataProducts) -> str:
        """Construct the API endpoint URL based on the data product and settings.
        This method handles path parameters by looking for placeholders in the endpoint template and
        replacing them with values from self.input or settings.resource_id.
        :param data_product: The SimployerDataProducts enum value indicating which API endpoint to target.
        :return: The full URL for the API request.
        """
        base_endpoint = EndpointInfo.get_endpoint_for_product(data_product)
        if base_endpoint is None:
            raise ValueError(f"Cannot build URL: data_product '{data_product.value}' is not supported.")

        host = self.linked_service.settings.host.rstrip("/")

        endpoint = base_endpoint
        pattern = re.compile(r"{([^}]+)}")
        matches = pattern.findall(base_endpoint)
        if matches:
            for param_name in matches:
                param_value = None
                #   First try to get the value from self.input if available
                if hasattr(self, "input") and self.input is not None and not self.input.empty:
                    if param_name in self.input.columns:
                        param_value = self.input.iloc[0][param_name]
                #  Next, try to get the value from settings.resource_id if not found in inputi
                elif hasattr(self.settings, "resource_id") and self.settings.resource_id:
                    param_value = self.settings.resource_id
                if param_value is None:
                    raise ReadError(f"Cannot build URL: path parameter '{{{param_name}}}' requires a value but none was provided.")
                endpoint = endpoint.replace(f"{{{param_name}}}", str(param_value))
        return f"{host}{endpoint}"
