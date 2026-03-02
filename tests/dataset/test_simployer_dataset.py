"""Unit tests for SimployerDataset."""

from unittest.mock import MagicMock
from uuid import uuid4

import pandas as pd
import pytest
from ds_resource_plugin_py_lib.common.resource.dataset.errors import ReadError
from ds_resource_plugin_py_lib.common.resource.errors import NotSupportedError

from ds_provider_simployer_py_lib.dataset.simployer import (
    ReadSettings,
    SimployerDataset,
    SimployerDatasetSettings,
)
from ds_provider_simployer_py_lib.enums import ResourceType, SimployerDataProducts
from ds_provider_simployer_py_lib.linked_service.simployer import SimployerLinkedService


class DummyResponse:
    """Mock HTTP response."""

    def __init__(self, json_data):
        self._json = json_data

    def json(self):
        return self._json


class DummySession:
    """Mock HTTP session that returns predefined responses."""

    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        self.requests = []

    def request(self, method, url, params):
        self.requests.append({"method": method, "url": url, "params": params})
        resp = self.responses[self.call_count]
        self.call_count += 1
        if isinstance(resp, Exception):
            raise resp
        return resp


class DummySimployerLinkedService(SimployerLinkedService):
    """Mock linked service with injected session."""

    def __init__(self, settings, session):
        super().__init__(id=uuid4(), name="dummy_name", version="1.0", settings=settings)
        self._session = session

    @property
    def session(self):
        return self._session


def make_linked_service(responses):
    """Create a mock linked service with predefined responses."""
    settings = MagicMock()
    settings.host = "https://hrconnect.simployer.com"
    return DummySimployerLinkedService(settings=settings, session=DummySession(responses))


def make_dataset(responses, data_product=SimployerDataProducts.EMPLOYEES, checkpoint=None):
    """Create a dataset with mocked linked service."""
    linked_service = make_linked_service(responses)
    settings = SimployerDatasetSettings(
        data_product=data_product,
        read=ReadSettings(page_size=100),
    )
    dataset = SimployerDataset(
        id=uuid4(),
        name="test_dataset",
        version="1.0",
        linked_service=linked_service,
        settings=settings,
    )
    if checkpoint is not None:
        dataset.checkpoint = checkpoint
    return dataset


# -----------------------------------------------------------------------------
# Contract: read() returns None, populates self.output
# -----------------------------------------------------------------------------


def test_read_returns_none():
    """read() must return None per contract."""
    responses = [DummyResponse({"records": [], "has_next_page": False})]
    dataset = make_dataset(responses)
    assert dataset.read() is None


def test_read_populates_output():
    """read() must populate self.output with a DataFrame."""
    responses = [DummyResponse({"records": [{"id": 1, "name": "Alice"}], "has_next_page": False})]
    dataset = make_dataset(responses)
    dataset.read()
    assert dataset.output is not None
    assert isinstance(dataset.output, pd.DataFrame)
    assert len(dataset.output) == 1
    assert dataset.output.iloc[0]["name"] == "Alice"


def test_read_single_page():
    """read() handles single page response correctly."""
    responses = [
        DummyResponse(
            {
                "records": [{"id": 1}, {"id": 2}],
                "has_next_page": False,
            }
        )
    ]
    dataset = make_dataset(responses)
    dataset.read()
    assert len(dataset.output) == 2


def test_read_multiple_pages():
    """read() handles pagination internally, concatenating all pages."""
    responses = [
        DummyResponse({"records": [{"id": 1}], "has_next_page": True}),
        DummyResponse({"records": [{"id": 2}], "has_next_page": True}),
        DummyResponse({"records": [{"id": 3}], "has_next_page": False}),
    ]
    dataset = make_dataset(responses)
    dataset.read()
    assert len(dataset.output) == 3
    assert list(dataset.output["id"]) == [1, 2, 3]


def test_read_empty_result():
    """read() returns empty DataFrame when no records exist (not an error)."""
    responses = [DummyResponse({"records": [], "has_next_page": False})]
    dataset = make_dataset(responses)
    dataset.read()
    assert dataset.output is not None
    assert isinstance(dataset.output, pd.DataFrame)
    assert len(dataset.output) == 0


# -----------------------------------------------------------------------------
# Contract: Error handling - wrap in ReadError with details
# -----------------------------------------------------------------------------


def test_read_wraps_exception_in_read_error():
    """Backend exceptions must be wrapped in ReadError with chaining."""
    responses = [Exception("Network failure")]
    dataset = make_dataset(responses)

    with pytest.raises(ReadError) as exc_info:
        dataset.read()

    assert "Failed to read data from Simployer API" in str(exc_info.value)
    assert exc_info.value.__cause__ is not None


def test_read_error_includes_details():
    """ReadError must include debugging details."""
    responses = [Exception("API error")]
    dataset = make_dataset(responses)

    with pytest.raises(ReadError) as exc_info:
        dataset.read()

    assert exc_info.value.details is not None
    assert "data_product" in exc_info.value.details
    assert "failed_page" in exc_info.value.details


def test_read_partial_results_on_error():
    """self.output may contain partial data when error occurs mid-pagination."""
    responses = [
        DummyResponse({"records": [{"id": 1}], "has_next_page": True}),
        DummyResponse({"records": [{"id": 2}], "has_next_page": True}),
        Exception("Failed on page 3"),
    ]
    dataset = make_dataset(responses)

    with pytest.raises(ReadError):
        dataset.read()

    # Partial results from pages 1 and 2 should be in output
    assert dataset.output is not None
    assert len(dataset.output) == 2


# -----------------------------------------------------------------------------
# Contract: Checkpoint support
# -----------------------------------------------------------------------------


def test_supports_checkpoint_returns_true():
    """supports_checkpoint property must return True."""
    responses = []
    dataset = make_dataset(responses)
    assert dataset.supports_checkpoint is True


def test_checkpoint_empty_means_full_load():
    """Empty checkpoint ({}) means full load starting from page 1."""
    responses = [DummyResponse({"records": [{"id": 1}], "has_next_page": False})]
    dataset = make_dataset(responses, checkpoint={})
    dataset.read()

    # Verify page parameter was 1
    request = dataset.linked_service.session.requests[0]
    assert request["params"]["page"] == 1


def test_checkpoint_populated_resumes():
    """Populated checkpoint resumes from last_page + 1."""
    responses = [DummyResponse({"records": [{"id": 5}], "has_next_page": False})]
    dataset = make_dataset(
        responses,
        checkpoint={"last_page": 3, "page_size": 100, "from_date": None, "to_date": None},
    )
    dataset.read()

    # Verify page parameter was 4 (3 + 1)
    request = dataset.linked_service.session.requests[0]
    assert request["params"]["page"] == 4


def test_checkpoint_updated_after_success():
    """Checkpoint is updated after successful read."""
    responses = [
        DummyResponse({"records": [{"id": 1}], "has_next_page": True}),
        DummyResponse({"records": [{"id": 2}], "has_next_page": False}),
    ]
    dataset = make_dataset(responses, checkpoint={})
    dataset.read()

    # Two pages read successfully, checkpoint should reflect last page and settings
    assert dataset.checkpoint["last_page"] == 1
    assert "page_size" in dataset.checkpoint
    assert "from_date" in dataset.checkpoint
    assert "to_date" in dataset.checkpoint


def test_checkpoint_on_error_reflects_last_successful_page():
    """On error, checkpoint reflects last successfully completed page."""
    responses = [
        DummyResponse({"records": [{"id": 1}], "has_next_page": True}),
        DummyResponse({"records": [{"id": 2}], "has_next_page": True}),
        Exception("Failed on page 3"),
    ]
    dataset = make_dataset(responses, checkpoint={})

    with pytest.raises(ReadError):
        dataset.read()

    # Pages 1 and 2 succeeded, failed on 3
    assert dataset.checkpoint["last_page"] == 2
    assert "page_size" in dataset.checkpoint


# -----------------------------------------------------------------------------
# Contract: type property
# -----------------------------------------------------------------------------


def test_type_property():
    """type property returns correct ResourceType."""
    responses = []
    dataset = make_dataset(responses)
    assert dataset.type == ResourceType.SIMPLOYER_DATASET


# -----------------------------------------------------------------------------
# Contract: Unsupported methods raise NotSupportedError
# -----------------------------------------------------------------------------


def test_create_raises_not_supported():
    """create() must raise NotSupportedError."""
    dataset = make_dataset([])
    with pytest.raises(NotSupportedError):
        dataset.create()


def test_update_raises_not_supported():
    """update() must raise NotSupportedError."""
    dataset = make_dataset([])
    with pytest.raises(NotSupportedError):
        dataset.update()


def test_upsert_raises_not_supported():
    """upsert() must raise NotSupportedError."""
    dataset = make_dataset([])
    with pytest.raises(NotSupportedError):
        dataset.upsert()


def test_delete_raises_not_supported():
    """delete() must raise NotSupportedError."""
    dataset = make_dataset([])
    with pytest.raises(NotSupportedError):
        dataset.delete()


def test_purge_raises_not_supported():
    """purge() must raise NotSupportedError."""
    dataset = make_dataset([])
    with pytest.raises(NotSupportedError):
        dataset.purge()


def test_list_raises_not_supported():
    """list() must raise NotSupportedError."""
    dataset = make_dataset([])
    with pytest.raises(NotSupportedError):
        dataset.list()


def test_rename_raises_not_supported():
    """rename() must raise NotSupportedError."""
    dataset = make_dataset([])
    with pytest.raises(NotSupportedError):
        dataset.rename()


def test_close_is_idempotent():
    """close() must not raise and can be called multiple times."""
    dataset = make_dataset([])
    # Should not raise
    dataset.close()
    dataset.close()
    dataset.close()
