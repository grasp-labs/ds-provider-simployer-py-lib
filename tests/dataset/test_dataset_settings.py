"""
**File:** ``test_dataset_settings.py``
**Region:** ``tests/dataset``

Description
-----------
SimployerDataset settings and initialization tests.

Covers:
- Dataset type property
- Settings initialization and default values
- HTTP method configuration
- Optional request parameters (data, json, params, headers)
"""

from uuid import uuid4

import pytest
from ds_resource_plugin_py_lib.common.resource.dataset import DatasetStorageFormatType
from ds_resource_plugin_py_lib.common.serde.deserialize import PandasDeserializer
from ds_resource_plugin_py_lib.common.serde.serialize import PandasSerializer

from ds_provider_simployer_py_lib.dataset.simployer import (
    SimployerDataset,
    SimployerDatasetSettings,
)
from ds_provider_simployer_py_lib.linked_service.simployer import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)


@pytest.fixture
def mock_linked_service():
    """Create a Simployer linked service for testing."""
    settings = SimployerLinkedServiceSettings(
        client_id="fake_test_client_id", client_secret="dummy_test_client_secret", host="https://api.example.com"
    )
    return SimployerLinkedService(
        settings=settings,
        id=uuid4(),
        name="test_service",
        version="1.0.0",
    )


def test_dataset_settings_defaults():
    """Test that dataset settings have correct default values."""
    settings = SimployerDatasetSettings(endpoint="/data")

    assert settings.endpoint == "/data"
    assert settings.method == "GET"
    assert settings.data is None
    assert settings.json is None
    assert settings.params is None
    assert settings.headers is None


def test_dataset_settings_with_post():
    """Test dataset settings with POST method and JSON body."""
    settings = SimployerDatasetSettings(
        endpoint="/data",
        method="POST",
        json={"name": "test"},
    )

    assert settings.endpoint == "/data"
    assert settings.method == "POST"
    assert settings.json == {"name": "test"}


def test_dataset_settings_with_query_params():
    """Test dataset settings with query parameters."""
    settings = SimployerDatasetSettings(
        endpoint="/data",
        params={"filter": "active", "limit": 10},
    )

    assert settings.endpoint == "/data"
    assert settings.method == "GET"
    assert settings.params == {"filter": "active", "limit": 10}


def test_dataset_settings_with_headers():
    """Test dataset settings with custom headers."""
    settings = SimployerDatasetSettings(
        endpoint="/data",
        headers={"X-Custom": "value"},
    )

    assert settings.endpoint == "/data"
    assert settings.method == "GET"
    assert settings.headers == {"X-Custom": "value"}


def test_dataset_settings_all_http_methods():
    """Test that all HTTP methods are valid."""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    for method in methods:
        settings = SimployerDatasetSettings(
            endpoint="/data",
            method=method,
        )
        assert settings.method == method


def test_dataset_type_property(mock_linked_service):
    """Test that dataset exposes correct type."""
    dataset = SimployerDataset(
        linked_service=mock_linked_service,
        settings=SimployerDatasetSettings(endpoint="/data"),
        id=uuid4(),
        name="test_dataset",
        version="1.0.0",
    )

    assert dataset.type.name == "SIMPLOYER_DATASET"
    assert dataset.type.value == "DS.RESOURCE.DATASET.SIMPLOYER"


def test_dataset_settings_initialization(mock_linked_service):
    """Test dataset initialization with settings."""
    settings = SimployerDatasetSettings(
        endpoint="/employees",
        method="GET",
        params={"department": "HR"},
    )

    dataset = SimployerDataset(
        linked_service=mock_linked_service,
        settings=settings,
        id=uuid4(),
        name="employee_dataset",
        version="1.0.0",
    )

    assert dataset.settings.endpoint == "/employees"
    assert dataset.settings.method == "GET"
    assert dataset.settings.params == {"department": "HR"}


def test_dataset_default_serializers(mock_linked_service):
    """Test that dataset has default Pandas serializers."""
    dataset = SimployerDataset(
        linked_service=mock_linked_service,
        settings=SimployerDatasetSettings(endpoint="/data"),
        id=uuid4(),
        name="test_dataset",
        version="1.0.0",
    )

    assert isinstance(dataset.serializer, PandasSerializer)
    assert isinstance(dataset.deserializer, PandasDeserializer)


def test_dataset_custom_serializers(mock_linked_service):
    """Test dataset with custom serializers."""
    custom_serializer = PandasSerializer(format=DatasetStorageFormatType.JSON)
    custom_deserializer = PandasDeserializer(format=DatasetStorageFormatType.JSON)

    dataset = SimployerDataset(
        linked_service=mock_linked_service,
        settings=SimployerDatasetSettings(endpoint="/data"),
        serializer=custom_serializer,
        deserializer=custom_deserializer,
        id=uuid4(),
        name="test_dataset",
        version="1.0.0",
    )

    assert dataset.serializer is custom_serializer
    assert dataset.deserializer is custom_deserializer


def test_dataset_settings_with_form_data():
    """Test dataset settings with form data (data parameter)."""
    settings = SimployerDatasetSettings(
        endpoint="/data",
        method="POST",
        data="form_encoded_data",
    )

    assert settings.endpoint == "/data"
    assert settings.method == "POST"
    assert settings.data == "form_encoded_data"


def test_dataset_settings_complex_json():
    """Test dataset settings with complex JSON body."""
    complex_json = {
        "filters": [
            {"field": "name", "value": "test"},
            {"field": "status", "value": "active"},
        ],
        "pagination": {"page": 1, "limit": 100},
    }

    settings = SimployerDatasetSettings(
        endpoint="/search",
        method="POST",
        json=complex_json,
    )

    assert settings.json == complex_json


def test_dataset_delete_not_implemented(mock_linked_service):
    """Test that delete operation raises NotImplementedError."""
    dataset = SimployerDataset(
        linked_service=mock_linked_service,
        settings=SimployerDatasetSettings(endpoint="/data"),
        id=uuid4(),
        name="test_dataset",
        version="1.0.0",
    )

    with pytest.raises(NotImplementedError, match="Delete operation is not supported"):
        dataset.delete()


def test_dataset_update_not_implemented(mock_linked_service):
    """Test that update operation raises NotImplementedError."""
    dataset = SimployerDataset(
        linked_service=mock_linked_service,
        settings=SimployerDatasetSettings(endpoint="/data"),
        id=uuid4(),
        name="test_dataset",
        version="1.0.0",
    )

    with pytest.raises(NotImplementedError, match="Update operation is not supported"):
        dataset.update()


def test_dataset_rename_not_implemented(mock_linked_service):
    """Test that rename operation raises NotImplementedError."""
    dataset = SimployerDataset(
        linked_service=mock_linked_service,
        settings=SimployerDatasetSettings(endpoint="/data"),
        id=uuid4(),
        name="test_dataset",
        version="1.0.0",
    )

    with pytest.raises(NotImplementedError, match="Rename operation is not supported"):
        dataset.rename()
