"""
**File:** ``simployer.py``
**Region:** ``ds_provider_simployer_py_lib/dataset/simployer.py``

Simployer Dataset

This module implements a dataset for Simployer APIs.

Example:
    >>> dataset = SimployerDataset(
    ...     deserializer=PandasDeserializer(format=DatasetStorageFormatType.JSON),
    ...     serializer=PandasSerializer(format=DatasetStorageFormatType.JSON),
    ...     settings=SimployerDatasetSettings(
    ...         endpoint="/data",
    ...         method="GET",
    ...     ),
    ...     linked_service=SimployerLinkedService(
    ...         settings=SimployerLinkedServiceSettings(
    ...             host="https://api.example.com",
    ...             client_id="your_client_id",
    ...             client_secret="your_client_secret",
    ...         ),
    ...     ),
    ... )
    >>> dataset.read()
    >>> data = dataset.output
"""

import builtins
from dataclasses import dataclass, field
from typing import Any, Generic, NoReturn, TypeVar

import pandas as pd
import requests
from ds_common_logger_py_lib import Logger
from ds_resource_plugin_py_lib.common.resource.dataset import (
    DatasetSettings,
    DatasetStorageFormatType,
    TabularDataset,
)
from ds_resource_plugin_py_lib.common.resource.dataset.errors import (
    CreateError,
    ReadError,
)
from ds_resource_plugin_py_lib.common.resource.errors import ResourceException
from ds_resource_plugin_py_lib.common.resource.linked_service.errors import (
    AuthenticationError,
    AuthorizationError,
)
from ds_resource_plugin_py_lib.common.resource.linked_service.errors import (
    ConnectionError as LinkedServiceConnectionError,
)
from ds_resource_plugin_py_lib.common.serde.deserialize import PandasDeserializer
from ds_resource_plugin_py_lib.common.serde.serialize import PandasSerializer

from ..enums import HttpMethod, ResourceType
from ..linked_service.simployer import SimployerLinkedService

logger = Logger.get_logger(__name__, package=True)


@dataclass(kw_only=True)
class SimployerDatasetSettings(DatasetSettings):
    """Settings for Simployer dataset."""

    method: HttpMethod = HttpMethod.GET
    """HTTP method to use for the request, e.g., GET, POST, PUT, DELETE, PATCH."""

    endpoint: str
    """API endpoint to interact with, e.g., '/data'."""

    data: Any | None = None
    """Data to send in the body of the request."""

    json: dict[str, Any] | None = None
    """JSON data to send in the body of the request."""

    files: list[Any] | None = None
    """Files to send in the request."""

    params: dict[str, Any] | None = None
    """Parameters to include in the request URL."""

    headers: dict[str, Any] | None = None
    """Headers to include in the request."""


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
    TabularDataset[
        SimployerLinkedServiceType,
        SimployerDatasetSettingsType,
        PandasSerializer,
        PandasDeserializer,
    ],
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

    def _send_request(self, error_cls: builtins.type[CreateError] | builtins.type[ReadError], **kwargs: Any) -> requests.Response:
        """
        Send an HTTP request to the Simployer API.

        Args:
            error_cls: The error class to raise for non-auth errors (CreateError or ReadError).
            kwargs: Additional keyword arguments to pass to the request.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            AuthenticationError: If authentication fails (401).
            AuthorizationError: If authorization fails (403).
            LinkedServiceConnectionError: If session is not initialized.
            error_cls: For other HTTP errors or request failures.
        """
        try:
            session = self.linked_service.session
        except LinkedServiceConnectionError as exc:
            raise LinkedServiceConnectionError(
                message="Failed to establish connection to linked service",
                details={"type": self.linked_service.type.value},
            ) from exc

        host = (self.linked_service.settings.host or "").rstrip("/")
        api_version = str(self.linked_service.settings.api_version or "").strip("/")
        endpoint = str(self.settings.endpoint or "")
        if endpoint and not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{host}/api/{api_version}{endpoint}"

        logger.debug("Sending %s request to %s", self.settings.method, url)

        # Merge headers
        request_headers = dict(self.settings.headers or {})

        try:
            response = session.request(
                method=self.settings.method,
                url=url,
                data=self.settings.data,
                json=self.settings.json,
                files=self.settings.files,
                params=self.settings.params,
                headers=request_headers if request_headers else None,
                timeout=self.linked_service.settings.timeout_seconds or 30,
                **kwargs,
            )
            response.raise_for_status()
            return response
        except requests.HTTPError as exc:
            status_code: int = exc.response.status_code if exc.response else 0
            if status_code == 401:
                raise AuthenticationError(
                    message="Authentication failed",
                    status_code=status_code,
                    details={"type": self.type.value, "url": url},
                ) from exc
            elif status_code == 403:
                raise AuthorizationError(
                    message="Authorization failed",
                    status_code=status_code,
                    details={"type": self.type.value, "url": url},
                ) from exc
            else:
                raise error_cls(
                    message=f"HTTP error occurred: {exc}",
                    status_code=status_code or 0,
                    details={"type": self.type.value, "url": url},
                ) from exc
        except requests.RequestException as exc:
            raise error_cls(
                message=f"Request failed: {exc}",
                details={"type": self.type.value, "url": url},
            ) from exc
        except ResourceException as exc:
            exc.details.update({"type": self.type.value})
            raise error_cls(
                message=exc.message,
                status_code=exc.status_code or 0,
                details=exc.details,
            ) from exc

    def create(self, **kwargs: Any) -> None:
        """
        Create data at the specified endpoint.

        Args:
            kwargs: Additional keyword arguments to pass to the request.

        Raises:
            AuthenticationError: If the authentication fails.
            AuthorizationError: If the authorization fails.
            ConnectionError: If the connection fails.
            CreateError: If the create error occurs.
        """
        response = self._send_request(CreateError, **kwargs)

        if response.content and self.deserializer:
            self.output = self.deserializer(response.content)
            self._set_schema(self.output)
        else:
            self.output = pd.DataFrame()

    def read(self, **kwargs: Any) -> None:
        """
        Read data from the specified endpoint.

        Args:
            kwargs: Additional keyword arguments to pass to the request.

        Raises:
            AuthenticationError: If the authentication fails.
            AuthorizationError: If the authorization fails.
            ConnectionError: If the connection fails.
            ReadError: If the read error occurs.
        """
        response = self._send_request(ReadError, **kwargs)

        if response.content and self.deserializer:
            self.output = self.deserializer(response.content)
            self._set_schema(self.output)
            self.next = self.deserializer.get_next(response.content)
            if self.next:
                self.cursor = self.deserializer.get_end_cursor(response.content)
        else:
            self.next = False
            self.cursor = None
            self.output = pd.DataFrame()

    def delete(self, **kwargs: Any) -> NoReturn:

        raise NotImplementedError("Delete operation is not supported for Simployer datasets")

    def update(self, **kwargs: Any) -> NoReturn:
        raise NotImplementedError("Update operation is not supported for Simployer datasets")

    def rename(self, **kwargs: Any) -> NoReturn:
        raise NotImplementedError("Rename operation is not supported for Simployer datasets")

    def close(self) -> None:
        """
        Close the dataset.
        """
        self.linked_service.close()

    def _set_schema(self, content: pd.DataFrame) -> None:
        """
        Set the schema from the content.

        Args:
            content: The content to set the schema from.
        """
        dtypes = content.convert_dtypes(dtype_backend="pyarrow").dtypes.to_dict()
        self.schema = {str(col): str(dtype) for col, dtype in dtypes.items()}
