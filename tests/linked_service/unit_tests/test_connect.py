"""
**File:** ``test_connect.py``
**Region:** ``tests/linked_service/unit_tests``

Description
-----------
Unit tests for Simployer linked service connection testing, focusing on exception handling.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from ds_provider_simployer_py_lib.linked_service import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.Session")
@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_connect_success(mock_post, mock_session):
    """
    test_connect_success

    :param mock_post: Description
    :param mock_session: Description
    """
    # Mock the token response
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake-token"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    # Mock the session
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance

    settings = SimployerLinkedServiceSettings(
        client_id="id", client_secret="secret", host="https://example.com", auth_type="OAUTH2"
    )
    service = SimployerLinkedService(settings=settings, id=uuid4(), name="test", version="1.0.0", description="desc")

    service.connect()

    # Check token was requested
    mock_post.assert_called_once()
    # Check session was created and headers updated
    mock_session_instance.headers.update.assert_called_once()


@patch("ds_provider_simployer_py_lib.linked_service.simployer.requests.post")
def test_connect_token_failure(mock_post):
    """
    Docstring for test_connect_token_failure

    :param mock_post: Description
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    settings = SimployerLinkedServiceSettings(
        client_id="id", client_secret="secret", host="https://example.com", auth_type="OAUTH2"
    )
    service = SimployerLinkedService(settings=settings, id=uuid4(), name="test", version="1.0.0", description="desc")

    with pytest.raises(ConnectionError, match="Access token not found"):
        service.connect()
