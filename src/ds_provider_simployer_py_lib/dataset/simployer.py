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
    DeleteError,
    ReadError,
    UpdateError,
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

    resource_id: str | None = None
    """For read operations, if set, indicates a single resource lookup by ID (e.g., /v1/persons/{id}).
    If None, read() performs based on read settings (pagination, filters, etc.) on the collection endpoint (e.g., /v1/employees).
    Note: Not all data products support single-record lookup.
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
        if self.settings.read.resource_id:
            self._read_single_resource(session)
            return

        # Collection read with pagination
        self._read_collection(session)

    def _read_single_resource(self, session: Any) -> None:
        """Fetch a single resource by ID."""
        resource_id = self.settings.read.resource_id
        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")
        url = self._build_url(self.settings.data_product, mode="read")
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
        """Fetch collection with pagination and update checkpoint with max 'updated' value."""
        # If checkpoint has from_date, set it in settings for incremental load
        if self.checkpoint and "from_date" in self.checkpoint:
            self.settings.read.from_date = self.checkpoint["from_date"]

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
            logger.error("Failed to read data from Simployer API: %s", exc)
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
        url = self._build_url(self.settings.data_product, mode="create")
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
        """
        Delete rows from Simployer API.

        Reads from self.input (which must be a pandas DataFrame) and issues a DELETE to the configured endpoint.
        Results are stored in self.output.

        Capacity Limit:
            The Simployer API accepts only 1 record per DELETE request.
            If self.input contains more than 1 row, this method raises DeleteError.
            The caller must batch: split self.input into single-row chunks and call delete() once per chunk.

        Input Requirement:
            - self.input must be a pandas DataFrame.
            - Only one record per delete() call is allowed (one row in the DataFrame).
            - Users must convert their data (dict, JSON, etc.) to a DataFrame before assigning to self.input.

        Example:
            import pandas as pd
            dataset.input = pd.DataFrame([{"id": "12345"}])
            dataset.delete()

        Per contract:
            - Empty input is a no-op (returns immediately without contacting the backend).
            - Deleting a row that does not exist is not an error and is idempotent.

        Raises:
            NotSupportedError: If the configured data product does not support delete (DELETE).
            DeleteError: If the input exceeds capacity (more than 1 row) or if deletion fails.
        """
        if self.input is None or self.input.empty:
            logger.info("No input data to delete, returning empty output")
            self.output = pd.DataFrame()
            return

        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")
        if not EndpointInfo.supports_method(self.settings.data_product, "DELETE"):
            raise NotSupportedError(f"Delete (DELETE) not supported for data product '{self.settings.data_product.value}'.")

        # Capacity limit: Simployer accepts 1 record per DELETE for atomicity
        if len(self.input) > 1:
            raise DeleteError(
                message="Simployer API accepts 1 record per request. Caller must batch.",
                details={"input_rows": len(self.input), "capacity": 1},
            )

        url = self._build_url(self.settings.data_product, mode="delete")
        logger.info("Deleting resource at %s", url)
        session = self.linked_service.connection
        try:
            response = session.delete(url=url)
            result = response.json() if response.content else None
            if result:
                self.output = pd.DataFrame([result] if isinstance(result, dict) else result)
            else:
                self.output = self.input.copy()
        except Exception as exc:
            logger.error("Failed to delete resource: %s", exc)
            raise DeleteError(
                message=f"Failed to delete {self.settings.data_product.value}",
                details={"data_product": self.settings.data_product.value},
            ) from exc

    def update(self) -> None:
        """
        Update an existing row in Simployer API.

        Reads from self.input (which must be a pandas DataFrame) and PUTs to the configured endpoint.
        Results are stored in self.output.

        Capacity Limit:
            The Simployer API accepts only 1 record per PUT request.
            If self.input contains more than 1 row, this method raises UpdateError.
            The caller must batch: split self.input into single-row chunks and call update() once per chunk.

        Input Requirement:
            - self.input must be a pandas DataFrame with one row.
            - Only one record per update() call is allowed (one row in the DataFrame).
            - Users must convert their data (dict, JSON, etc.) to a DataFrame before assigning to self.input.

        Example:
            import pandas as pd
            dataset.input = pd.DataFrame([{"id": "12345", "status": "active"}])
            dataset.update()

        Per contract:
            - Empty input is a no-op (returns immediately without contacting the backend).
            - Must not insert new rows (non-existent resources result in an error).
            - Idempotent: Yes. Updating a row to the same values has no effect.

        Raises:
            NotSupportedError: If the configured data product does not support update (PUT).
            UpdateError: If the input exceeds capacity (more than 1 row) or if the update fails.
        """
        if self.input is None or self.input.empty:
            logger.info("No input data to update, returning empty output")
            self.output = pd.DataFrame()
            return

        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")
        if not EndpointInfo.supports_method(self.settings.data_product, "PUT"):
            raise NotSupportedError(f"Update (PUT) not supported for data product '{self.settings.data_product.value}'.")

        # Capacity limit: Simployer accepts 1 record per PUT for atomicity
        if len(self.input) > 1:
            raise UpdateError(
                message="Simployer API accepts 1 record per request. Caller must batch.",
                details={"input_rows": len(self.input), "capacity": 1},
            )

        # Don't mutate self.input - work on copy
        row = self.input.iloc[0].to_dict()

        session = self.linked_service.connection
        url = self._build_url(self.settings.data_product, mode="update")
        logger.info("Updating resource at %s", url)

        try:
            response = session.put(url=url, json=row)
            status = response.status_code
            status_map = {
                404: "NotFoundError",
                400: "BadRequest",
                401: "Unauthorized",
            }

            if status in status_map:
                raise UpdateError(
                    message=f"Failed to update {self.settings.data_product.value}",
                    details={"status": status, "error": status_map[status], "detail": response.text},
                )
            elif status in (200, 201, 204):
                if response.content:
                    try:
                        result = response.json()
                        self.output = pd.DataFrame([result] if isinstance(result, dict) else result)
                    except ValueError:
                        logger.warning("Non-JSON response for successful update: %s", response.text)
                        self.output = self.input.copy()
                else:
                    self.output = self.input.copy()
            else:
                raise UpdateError(
                    message=f"Failed to update {self.settings.data_product.value}",
                    details={"status": status, "detail": response.text},
                )
        except UpdateError:
            raise
        except Exception as exc:
            logger.error("Failed to update resource: %s", exc)
            raise UpdateError(
                message=f"Failed to update {self.settings.data_product.value}",
                details={"data_product": self.settings.data_product.value},
            ) from exc

    def close(self) -> None:
        """Release any resources held by the dataset.

        For Simployer, the dataset holds no resources directly.
        Connection lifecycle is managed by the linked service.
        """

    def rename(self) -> None:
        raise NotSupportedError("Method (rename) not supported by Simployer provider.")

    def list(self) -> None:
        raise NotSupportedError("Method (list) not supported by Simployer provider.")

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
        """Build checkpoint dictionary for incremental load support.

        Sets from_date to the ISO-8601 string representation of the maximum 'updated'
        value in self.output if available. This ensures the checkpoint is JSON-serializable.

        Checkpoint structure:
            {
                "last_page": int,
                "page_size": int,
                "to_date": str | None (ISO-8601 format),
                "from_date": str | None (ISO-8601 format),
                "data_product": str
            }
        """
        if self.settings.data_product is None:
            raise NotSupportedError("Data product must be specified.")
        checkpoint = {
            "last_page": last_page,
            "page_size": self.settings.read.page_size,
            "to_date": self.settings.read.to_date,
            "data_product": self.settings.data_product.value,
            "from_date": None,
        }
        # Set from_date from max 'updated' in self.output if available
        if (
            hasattr(self, "output")
            and isinstance(self.output, pd.DataFrame)
            and not self.output.empty
            and "updated" in self.output.columns
        ):
            updated_values = self.output["updated"].dropna()
            if not updated_values.empty:
                max_updated = updated_values.max()
                # Convert pandas.Timestamp to ISO-8601 string for JSON serialization
                # (if it's already a string, use it as-is)
                if pd.notna(max_updated):
                    if isinstance(max_updated, str):
                        checkpoint["from_date"] = max_updated
                    else:
                        checkpoint["from_date"] = max_updated.isoformat()
        return checkpoint

    def _build_url(self, data_product: SimployerDataProducts, mode: str = "read") -> str:
        """Construct the API endpoint URL based on the data product and operation mode.
        Handles path parameters for read, create, update, and delete operations.
        :param data_product: The SimployerDataProducts enum value indicating which API endpoint to target.
        :param mode: Operation mode ("read", "create", "update", "delete").
        :return: The full URL for the API request.
        :raises ReadError: If mode is "read" and endpoint is missing or parameter cannot be resolved.
        :raises CreateError: If mode is "create" and endpoint is missing or parameter cannot be resolved.
        :raises UpdateError: If mode is "update" and endpoint is missing or parameter cannot be resolved.
        :raises DeleteError: If mode is "delete" and endpoint is missing or parameter cannot be resolved.
        """
        # Map mode to the appropriate error class
        error_map = {
            "read": ReadError,
            "create": CreateError,
            "update": UpdateError,
            "delete": DeleteError,
        }
        error_class = error_map.get(mode, ReadError)

        base_endpoint = EndpointInfo.get_endpoint_for_product(data_product)
        if base_endpoint is None:
            raise error_class(message=f"No endpoint configured for data product '{data_product!s}'.")

        host = self.linked_service.settings.host.rstrip("/")
        endpoint = base_endpoint
        pattern = re.compile(r"{([^}]+)}")
        matches = pattern.findall(base_endpoint)
        if matches:
            for param_name in matches:
                param_value = None
                if mode in ("create", "delete", "update"):
                    if (
                        hasattr(self, "input")
                        and self.input is not None
                        and not self.input.empty
                        and param_name in self.input.columns
                    ):
                        param_value = self.input.iloc[0][param_name]
                elif mode == "read" and hasattr(self.settings.read, "resource_id") and self.settings.read.resource_id:
                    param_value = self.settings.read.resource_id
                if param_value is None:
                    raise error_class(
                        message=(
                            f"Cannot build URL: path parameter '{{{param_name}}}' requires a value "
                            f"but none was provided for mode '{mode}'."
                        )
                    )
                endpoint = endpoint.replace(f"{{{param_name}}}", str(param_value))
        elif mode == "read" and hasattr(self.settings.read, "resource_id") and self.settings.read.resource_id:
            endpoint = f"{endpoint}/{self.settings.read.resource_id}"
        return f"{host}{endpoint}"
