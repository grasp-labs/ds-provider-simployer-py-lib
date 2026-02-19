"""
**File:** ``test_connect.py``
**Region:** ``tests/linked_service/integration``

Integration Tests for Simployer Linked Service
================================================

Description
-----------
Integration tests that verify the SimployerLinkedService can connect to and interact with
a real Simployer API instance using client credentials.
These tests are inherited from HttpLinkedService and focus on testing the Simployer-specific configuration.

Prerequisites
-------------
To run these integration tests, you need to set the following environment variables:

Required:
    - SIMPLOYER_CLIENT_ID: Your Simployer client ID
    - SIMPLOYER_CLIENT_SECRET: Your Simployer client secret

Optional (with defaults):
    - SIMPLOYER_HOST: Simployer API host (default: https://hrconnect.simployer.com)
    - SIMPLOYER_TOKEN_ENDPOINT: Token endpoint (default: https://simplauth.simployer.com/oauth/token)
    - SIMPLOYER_AUDIENCE: Audience identifier (default: https://hrconnect.simployer.com)

Status
------
Tests will be skipped if SIMPLOYER_CLIENT_ID and SIMPLOYER_CLIENT_SECRET are not provided.
"""

import os
from uuid import uuid4

import pytest

from ds_provider_simployer_py_lib.enums import ResourceType
from ds_provider_simployer_py_lib.linked_service import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)

# Skip all tests in this module if credentials are not provided
pytestmark = pytest.mark.skipif(
    not os.getenv("SIMPLOYER_CLIENT_ID") or not os.getenv("SIMPLOYER_CLIENT_SECRET"),
    reason="SIMPLOYER_CLIENT_ID and SIMPLOYER_CLIENT_SECRET environment variables are required for integration tests",
)


def make_settings_from_env():
    """Create settings from environment variables for integration testing."""
    return SimployerLinkedServiceSettings(
        client_id=os.getenv("SIMPLOYER_CLIENT_ID", ""),
        client_secret=os.getenv("SIMPLOYER_CLIENT_SECRET", ""),
        host=os.getenv("SIMPLOYER_HOST", "https://hrconnect.simployer.com"),
        token_endpoint=os.getenv("SIMPLOYER_TOKEN_ENDPOINT", "https://simplauth.simployer.com/oauth/token"),
        audience=os.getenv("SIMPLOYER_AUDIENCE", "https://hrconnect.simployer.com"),
        api_version=os.getenv("SIMPLOYER_API_VERSION", "v1"),
    )


def make_service_from_env():
    """Create a SimployerLinkedService instance from environment variables."""
    return SimployerLinkedService(
        settings=make_settings_from_env(),
        id=uuid4(),
        name="integration-test",
        version="1.0.0",
        description="Integration test service",
    )


class TestSimployerLinkedServiceIntegration:
    """Integration tests for SimployerLinkedService with real Simployer API.

    Tests verify that the simplified HttpLinkedService-based implementation
    correctly authenticates and connects to Simployer.
    """

    def test_test_connection_success(self):
        """Test that test_connection succeeds with valid credentials."""
        service = make_service_from_env()
        success, message = service.test_connection()
        assert success is True, f"Connection should succeed but got: {message}"

    def test_service_type(self):
        """Test that linked service type is correctly identified."""
        service = make_service_from_env()
        assert service.type == ResourceType.SIMPLOYER_LINKED_SERVICE

    def test_settings_custom_auth_configured(self):
        """Test that custom authentication settings are properly configured."""
        service = make_service_from_env()
        assert service.settings.custom is not None
        assert service.settings.custom.token_endpoint == service.settings.token_endpoint
        assert service.settings.custom.data["client_id"] == service.settings.client_id
        assert service.settings.custom.data["audience"] == service.settings.audience
        assert service.settings.custom.data["grant_type"] == "client_credentials"
