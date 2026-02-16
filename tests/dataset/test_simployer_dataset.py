"""
**File:** ``test_simployer_dataset.py``
**Region:** ``tests/dataset``

Description
-----------
Unit tests for Simployer dataset implementation, covering read, create, request handling, and error scenarios.
"""

from unittest.mock import MagicMock, PropertyMock
from uuid import uuid4

import pandas as pd
import pytest
import requests
from ds_resource_plugin_py_lib.common.resource.dataset import DatasetStorageFormatType
from ds_resource_plugin_py_lib.common.resource.dataset.errors import ReadError
from ds_resource_plugin_py_lib.common.resource.linked_service.errors import (
    AuthenticationError,
    AuthorizationError,
)
from ds_resource_plugin_py_lib.common.resource.linked_service.errors import (
    ConnectionError as LinkedServiceConnectionError,
)
from ds_resource_plugin_py_lib.common.serde.deserialize import PandasDeserializer
from ds_resource_plugin_py_lib.common.serde.serialize import PandasSerializer

from ds_provider_simployer_py_lib.dataset.simployer import (
    SimployerDataset,
    SimployerDatasetSettings,
)
from ds_provider_simployer_py_lib.linked_service.simployer import SimployerLinkedService


@pytest.fixture
def mock_linked_service():
    """Create a mock linked service."""
    mock_service = MagicMock(spec=SimployerLinkedService)
    mock_service.type = MagicMock()
    mock_service.type.value = "DS.RESOURCE.DATASET.SIMPLOYER"

    # Mock settings object
    mock_settings = MagicMock()
    mock_settings.host = "https://api.example.com"
    mock_settings.api_version = "v1"
    mock_settings.timeout_seconds = 30
    mock_service.settings = mock_settings

    return mock_service


@pytest.fixture
def dataset_settings():
    """Create dataset settings."""
    return SimployerDatasetSettings(
        endpoint="/data",
        method="GET",
    )


@pytest.fixture
def simployer_dataset(mock_linked_service, dataset_settings):
    """Create a Simployer dataset instance."""
    return SimployerDataset(
        linked_service=mock_linked_service,
        settings=dataset_settings,
        serializer=PandasSerializer(format=DatasetStorageFormatType.JSON),
        deserializer=PandasDeserializer(format=DatasetStorageFormatType.JSON),
        id=uuid4(),
        name="test_dataset",
        version="1.0.0",
    )


class TestSimployerDatasetRead:
    """Tests for the read method."""

    def test_read_success(self, simployer_dataset, mock_linked_service):
        """Test successful data read."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b'[{"id": 1, "name": "test"}]'
        mock_response.raise_for_status.return_value = None

        # Mock session
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        # Mock deserializer
        mock_df = pd.DataFrame({"id": [1], "name": ["test"]})
        simployer_dataset.deserializer = MagicMock()
        simployer_dataset.deserializer.return_value = mock_df
        simployer_dataset.deserializer.get_next.return_value = False
        simployer_dataset.deserializer.get_end_cursor.return_value = None

        simployer_dataset.read()

        # Verify session.request was called correctly
        mock_session.request.assert_called_once()
        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["method"] == "GET"
        assert call_kwargs["url"] == "https://api.example.com/api/v1/data"
        assert call_kwargs["timeout"] == 30

        # Verify output is set
        assert simployer_dataset.output.equals(mock_df)
        assert simployer_dataset.next is False

    def test_read_with_pagination(self, simployer_dataset, mock_linked_service):
        """Test read with pagination cursor."""
        mock_response = MagicMock()
        mock_response.content = b'[{"id": 1}]'
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        mock_df = pd.DataFrame({"id": [1]})
        simployer_dataset.deserializer = MagicMock()
        simployer_dataset.deserializer.return_value = mock_df
        simployer_dataset.deserializer.get_next.return_value = True
        simployer_dataset.deserializer.get_end_cursor.return_value = "next_cursor_123"

        simployer_dataset.read()

        assert simployer_dataset.next is True
        assert simployer_dataset.cursor == "next_cursor_123"

    def test_read_authentication_error(self, simployer_dataset, mock_linked_service):
        """Test read with authentication error (401)."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_exception = requests.HTTPError()
        mock_exception.response = mock_response
        mock_response.raise_for_status.side_effect = mock_exception

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        with pytest.raises(AuthenticationError) as exc_info:
            simployer_dataset.read()

        assert exc_info.value.message == "Authentication failed"
        assert exc_info.value.status_code == 401

    def test_read_authorization_error(self, simployer_dataset, mock_linked_service):
        """Test read with authorization error (403)."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_exception = requests.HTTPError()
        mock_exception.response = mock_response
        mock_response.raise_for_status.side_effect = mock_exception

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        with pytest.raises(AuthorizationError) as exc_info:
            simployer_dataset.read()

        assert exc_info.value.message == "Authorization failed"
        assert exc_info.value.status_code == 403

    def test_read_http_error(self, simployer_dataset, mock_linked_service):
        """Test read with other HTTP errors (5xx)."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_exception = requests.HTTPError()
        mock_exception.response = mock_response
        mock_response.raise_for_status.side_effect = mock_exception

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        with pytest.raises(ReadError) as exc_info:
            simployer_dataset.read()

        assert "HTTP error occurred" in exc_info.value.message
        assert exc_info.value.status_code == 500

    def test_read_request_exception(self, simployer_dataset, mock_linked_service):
        """Test read with request exception."""
        mock_session = MagicMock()
        mock_session.request.side_effect = requests.RequestException("Connection timeout")
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        with pytest.raises(ReadError) as exc_info:
            simployer_dataset.read()

        assert "Request failed" in exc_info.value.message

    def test_read_empty_response(self, simployer_dataset, mock_linked_service):
        """Test read with empty response content."""
        mock_response = MagicMock()
        mock_response.content = b""
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        simployer_dataset.read()

        # Should create empty DataFrame
        assert isinstance(simployer_dataset.output, pd.DataFrame)
        assert len(simployer_dataset.output) == 0
        assert simployer_dataset.next is False

    def test_read_not_connected(self, simployer_dataset, mock_linked_service):
        """Test read when not connected to linked service."""
        type(mock_linked_service).session = PropertyMock(
            side_effect=LinkedServiceConnectionError(
                message="Not connected",
                status_code=0,
                details={},
            )
        )

        with pytest.raises(LinkedServiceConnectionError):
            simployer_dataset.read()


class TestSimployerDatasetCreate:
    """Tests for the create method."""

    def test_create_success(self, simployer_dataset, mock_linked_service):
        """Test successful data creation."""
        mock_response = MagicMock()
        mock_response.content = b'{"id": 123}'
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        mock_df = pd.DataFrame({"id": [123]})
        simployer_dataset.deserializer = MagicMock()
        simployer_dataset.deserializer.return_value = mock_df

        simployer_dataset.create()

        mock_session.request.assert_called_once()
        assert simployer_dataset.output.equals(mock_df)

    def test_create_with_post_method(self, mock_linked_service):
        """Test create with POST method and request body."""
        settings = SimployerDatasetSettings(
            endpoint="/data",
            method="POST",
            json={"name": "test_data"},
        )
        dataset = SimployerDataset(
            linked_service=mock_linked_service,
            settings=settings,
            id=uuid4(),
            name="test",
            version="1.0.0",
        )

        mock_response = MagicMock()
        mock_response.content = b"{}"
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        dataset.deserializer = MagicMock()
        dataset.deserializer.return_value = pd.DataFrame()

        dataset.create()

        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["method"] == "POST"
        assert call_kwargs["json"] == {"name": "test_data"}

    def test_create_authentication_error(self, simployer_dataset, mock_linked_service):
        """Test create with authentication error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_exception = requests.HTTPError()
        mock_exception.response = mock_response
        mock_response.raise_for_status.side_effect = mock_exception

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        with pytest.raises(AuthenticationError):
            simployer_dataset.create()


class TestSimployerDatasetSendRequest:
    """Tests for the _send_request method."""

    def test_send_request_url_construction(self, simployer_dataset, mock_linked_service):
        """Test correct URL construction with different endpoint formats."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        simployer_dataset._send_request(ReadError)

        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["url"] == "https://api.example.com/api/v1/data"

    def test_send_request_with_params(self, mock_linked_service):
        """Test send_request with query parameters."""
        settings = SimployerDatasetSettings(
            endpoint="/data",
            params={"filter": "active", "limit": 10},
        )
        dataset = SimployerDataset(
            linked_service=mock_linked_service,
            settings=settings,
            id=uuid4(),
            name="test",
            version="1.0.0",
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        dataset._send_request(ReadError)

        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["params"] == {"filter": "active", "limit": 10}

    def test_send_request_with_headers(self, mock_linked_service):
        """Test send_request with custom headers."""
        settings = SimployerDatasetSettings(
            endpoint="/data",
            headers={"X-Custom-Header": "value"},
        )
        dataset = SimployerDataset(
            linked_service=mock_linked_service,
            settings=settings,
            id=uuid4(),
            name="test",
            version="1.0.0",
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        dataset._send_request(ReadError)

        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["headers"] == {"X-Custom-Header": "value"}

    def test_send_request_endpoint_slash_handling(self, mock_linked_service):
        """Test endpoint with/without leading slash."""
        settings = SimployerDatasetSettings(endpoint="data")  # No leading slash
        dataset = SimployerDataset(
            linked_service=mock_linked_service,
            settings=settings,
            id=uuid4(),
            name="test",
            version="1.0.0",
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        type(mock_linked_service).session = PropertyMock(return_value=mock_session)

        dataset._send_request(ReadError)

        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["url"] == "https://api.example.com/api/v1/data"


class TestSimployerDatasetNotImplemented:
    """Tests for not-implemented operations."""

    def test_delete_not_implemented(self, simployer_dataset):
        """Test that delete raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            simployer_dataset.delete()

        assert "Delete operation is not supported" in str(exc_info.value)

    def test_update_not_implemented(self, simployer_dataset):
        """Test that update raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            simployer_dataset.update()

        assert "Update operation is not supported" in str(exc_info.value)

    def test_rename_not_implemented(self, simployer_dataset):
        """Test that rename raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            simployer_dataset.rename()

        assert "Rename operation is not supported" in str(exc_info.value)


class TestSimployerDatasetClose:
    """Tests for the close method."""

    def test_close_calls_linked_service_close(self, simployer_dataset, mock_linked_service):
        """Test that close calls linked_service.close()."""
        simployer_dataset.close()

        mock_linked_service.close.assert_called_once()


class TestSimployerDatasetSetSchema:
    """Tests for the _set_schema method."""

    def test_set_schema(self, simployer_dataset):
        """Test schema is correctly extracted from DataFrame."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["a", "b", "c"],
                "value": [1.5, 2.5, 3.5],
            }
        )

        simployer_dataset._set_schema(df)

        assert simployer_dataset.schema is not None
        assert "id" in simployer_dataset.schema
        assert "name" in simployer_dataset.schema
        assert "value" in simployer_dataset.schema


class TestSimployerDatasetProperties:
    """Tests for dataset properties."""

    def test_type_property(self, simployer_dataset):
        """Test type property returns correct ResourceType."""
        assert simployer_dataset.type.value == "DS.RESOURCE.DATASET.SIMPLOYER"

    def test_method_defaults(self):
        """Test default HTTP method is GET."""
        settings = SimployerDatasetSettings(endpoint="/data")
        assert settings.method == "GET"
