"""Unit tests for SimployerLinkedService."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import requests

from ds_provider_simployer_py_lib.linked_service import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)


def make_settings():
    """Create a SimployerLinkedServiceSettings instance for testing."""
    return SimployerLinkedServiceSettings(client_id="id", client_secret="secret", host="https://example.com", auth_type="OAUTH2")


def make_service():
    """Create a SimployerLinkedService instance for testing."""
    return SimployerLinkedService(settings=make_settings(), id=uuid4(), name="test", version="1.0.0", description="desc")


def test_type_property():
    """Test that the linked service type property returns the correct type."""
    service = make_service()
    assert service.type.name == "SIMPLOYER_LINKED_SERVICE"


def test_session_access_before_connect():
    """Test that accessing session before connect raises ConnectionError."""
    service = make_service()
    with pytest.raises(ConnectionError, match="Not connected"):
        _ = service.session


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.Session")
@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_connect_success(mock_post, mock_session):
    """Test that connect successfully acquires an access token."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "token"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    service = make_service()
    service.connect()
    assert service.session is mock_session_instance
    mock_session_instance.headers.update.assert_called_once()


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_connect_token_failure(mock_post):
    """Test that connect raises error when access token is not found."""
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    service = make_service()
    with pytest.raises(ConnectionError, match="Access token not found"):
        service.connect()


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_connect_invalid_json_response(mock_post):
    """Test handling of non-JSON auth response"""
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.headers.get.return_value = "text/html"
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    service = make_service()

    with pytest.raises(ConnectionError, match="Invalid authentication response"):
        service.connect()


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_connect_network_failure(mock_post):
    """Test handling of network failures"""
    mock_post.side_effect = requests.RequestException("Network error")

    service = make_service()

    with pytest.raises(ConnectionError, match="Failed to obtain access token"):
        service.connect()


def test_close_clears_session_and_token():
    """Test that close clears session and access token."""
    service = make_service()
    service._session = MagicMock()
    service._access_token = "token"
    service.close()
    assert service._session is None
    assert service._access_token is None


def test_test_connection_success():
    """Test that test_connection returns success status."""
    session_patch = "ds_provider_simployer_py_lib.linked_service.simployer.requests.Session"
    post_patch = "ds_provider_simployer_py_lib.linked_service.simployer.requests.post"
    with patch(session_patch) as mock_session, patch(post_patch) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        service = make_service()
        success, message = service.test_connection()
        assert success is True
        assert message == "Connection successfully tested"


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.Session")
@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_session_property_after_connect(mock_post, mock_session):
    """Test that session property returns correct session after connect."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "token"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    service = make_service()
    service.connect()
    # Should not raise
    assert service.session is mock_session_instance


def test_connect_missing_client_id():
    """Test that connect raises error when client_id is missing."""
    settings = make_settings()
    settings.client_id = ""
    service = SimployerLinkedService(settings=settings, id=uuid4(), name="test", version="1.0.0", description="desc")
    with pytest.raises(ConnectionError, match="Client ID is missing"):
        service.connect()


def test_connect_missing_client_secret():
    """Test that connect raises error when client_secret is missing."""
    settings = make_settings()
    settings.client_secret = ""
    service = SimployerLinkedService(settings=settings, id=uuid4(), name="test", version="1.0.0", description="desc")
    with pytest.raises(ConnectionError, match="Client secret is missing"):
        service.connect()


def test_connect_missing_host():
    """Test that connect raises error when host is missing."""
    settings = make_settings()
    settings.host = ""
    service = SimployerLinkedService(settings=settings, id=uuid4(), name="test", version="1.0.0", description="desc")
    with pytest.raises(ConnectionError, match="Host URL is missing"):
        service.connect()


def test_test_connection_error_path():
    """Test that test_connection handles connect errors gracefully."""
    service = make_service()

    def fail_connect():
        raise ConnectionError("fail connect")

    service.connect = fail_connect
    success, message = service.test_connection()
    assert success is False
    assert message == "fail connect"


def test_validate_settings_type_error():
    """Test that _validate_settings raises error for invalid settings."""
    service = make_service()
    service.settings = object()  # Not SimployerLinkedServiceSettings
    with pytest.raises(AttributeError, match="Settings not set correctly\\."):
        service._validate_settings()  # type: ignore[attr-defined]
