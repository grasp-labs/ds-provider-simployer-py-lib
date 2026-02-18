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


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.Session")
@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_close_clears_session_and_token(mock_post, mock_session):
    """Test that close clears session and access token."""
    # Setup a connected service
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "token"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance

    service = make_service()
    service.connect()

    # Verify connected
    assert service.is_connected is True

    # Close the connection
    service.close()

    # Verify disconnected
    assert service.is_connected is False
    with pytest.raises(ConnectionError, match="Not connected"):
        _ = service.session
    mock_session_instance.close.assert_called_once()


def test_test_connection_already_connected_valid_token():
    """Test that test_connection validates existing token without reconnecting."""
    session_patch = "ds_provider_simployer_py_lib.linked_service.simployer.requests.Session"
    post_patch = "ds_provider_simployer_py_lib.linked_service.simployer.requests.post"
    with patch(session_patch) as mock_session, patch(post_patch) as mock_post:
        # Setup initial connection
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        service = make_service()
        service.connect()
        connect_call_count = mock_post.call_count

        # Now test connection while already connected
        mock_head_response = MagicMock()
        mock_head_response.raise_for_status.return_value = None
        mock_session_instance.head.return_value = mock_head_response

        success, message = service.test_connection()

        # Should validate with HEAD request, not reconnect
        assert success is True
        assert message == "Connection successfully tested"
        mock_session_instance.head.assert_called_once()
        # post should not be called again (no new token)
        assert mock_post.call_count == connect_call_count


def test_test_connection_already_connected_invalid_token():
    """Test that test_connection raises error if token validation fails."""
    session_patch = "ds_provider_simployer_py_lib.linked_service.simployer.requests.Session"
    post_patch = "ds_provider_simployer_py_lib.linked_service.simployer.requests.post"
    with patch(session_patch) as mock_session, patch(post_patch) as mock_post:
        # Setup initial connection
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        service = make_service()
        service.connect()

        # Token validation fails
        mock_session_instance.head.side_effect = requests.RequestException("Unauthorized")

        # Should raise ConnectionError
        with pytest.raises(ConnectionError, match="Token validation failed"):
            service.test_connection()


# Token validation is tested indirectly through test_test_connection_already_connected_valid_token
# and test_test_connection_already_connected_invalid_token tests above


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


def test_test_connection_not_connected():
    """Test that test_connection raises error if not connected."""
    service = make_service()
    with pytest.raises(ConnectionError, match="Not connected"):
        service.test_connection()


def test_validate_settings_type_error():
    """Test that connect raises error for invalid settings type."""
    service = make_service()
    service.settings = object()  # type: ignore[assignment] - Not SimployerLinkedServiceSettings
    with pytest.raises(AttributeError, match="Invalid settings type: expected SimployerLinkedServiceSettings"):
        service.connect()  # _validate_settings is called internally
