"""
**File:** ``test_connect.py``
**Region:** ``tests/linked_service/integration``

Integration Tests for Simployer Linked Service
================================================

Description
-----------
Integration tests that verify the SimployerLinkedService can connect to and interact with
a real Simployer API instance. These tests require valid Simployer OAuth2 credentials.

Prerequisites
-------------
To run these integration tests, you need to set the following environment variables:

Required:
    - SIMPLOYER_CLIENT_ID: Your Simployer OAuth2 client ID
    - SIMPLOYER_CLIENT_SECRET: Your Simployer OAuth2 client secret

Optional (with defaults):
    - SIMPLOYER_HOST: Simployer API host (default: https://hrconnect.simployer.com)
    - SIMPLOYER_AUTH_URL: OAuth2 token endpoint (default: https://simplauth.simployer.com/oauth/token)
    - SIMPLOYER_AUDIENCE: OAuth2 audience (default: https://hrconnect.simployer.com)

Status
------
PLACEHOLDER: Awaiting Simployer credentials to enable integration tests.
Tests will be skipped if credentials are not provided.
"""

import os
from uuid import uuid4

import pytest

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
        auth_url=os.getenv("SIMPLOYER_AUTH_URL", "https://simplauth.simployer.com/oauth/token"),
        audience=os.getenv("SIMPLOYER_AUDIENCE", "https://hrconnect.simployer.com"),
        auth_type="OAUTH2",
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
    """Integration tests for SimployerLinkedService with real Simployer API."""

    def test_connect_and_session(self):
        """Test connecting to Simployer and accessing an authenticated session."""
        service = make_service_from_env()
        try:
            service.connect()
            # Verify session is active and properly authenticated
            assert service.session is not None, "Session should not be None after connect"
            assert service._access_token is not None, "Access token should not be None"
            assert "Authorization" in service.session.headers, "Authorization header should be present"
            assert service.session.headers["Authorization"].startswith("Bearer "), "Should use Bearer token"
        finally:
            service.close()

    def test_test_connection_success(self):
        """Test that test_connection succeeds with valid credentials."""
        service = make_service_from_env()
        success, message = service.test_connection()
        assert success is True, f"Connection should succeed but got: {message}"
        assert message == "Connection successfully tested"

    def test_session_isolation(self):
        """Test that multiple services maintain isolated sessions."""
        service1 = make_service_from_env()
        service2 = make_service_from_env()

        try:
            service1.connect()
            service2.connect()

            # Sessions should be different instances
            assert service1.session is not service2.session, "Each service should have its own session"
            # Both should have valid tokens
            assert service1._access_token is not None, "Service 1 should have access token"
            assert service2._access_token is not None, "Service 2 should have access token"
        finally:
            service1.close()
            service2.close()

    def test_close_clears_resources(self):
        """Test that close properly clears connection resources."""
        service = make_service_from_env()
        service.connect()

        # Verify connected before closing
        assert service._session is not None, "Session should exist after connect"
        assert service._access_token is not None, "Access token should exist after connect"

        service.close()

        # Verify resources are cleaned up
        assert service._session is None, "Session should be None after close"
        assert service._access_token is None, "Access token should be None after close"

    def test_reconnect_after_close(self):
        """Test that a service can successfully reconnect after being closed."""
        service = make_service_from_env()

        try:
            # First connection
            service.connect()
            first_token = service._access_token
            assert first_token is not None, "First connection should get a token"
            service.close()

            # Second connection (reconnect)
            service.connect()
            second_token = service._access_token
            assert second_token is not None, "Second connection should get a token"
            assert service.session is not None, "Session should be available after reconnect"
        finally:
            service.close()

    def test_service_type(self):
        """Test that linked service type is correctly identified."""
        service = make_service_from_env()
        assert service.type.name == "SIMPLOYER_LINKED_SERVICE"

    def test_session_contains_valid_bearer_token(self):
        """Test that the authenticated session includes a valid Bearer token."""
        service = make_service_from_env()
        try:
            service.connect()
            auth_header = service.session.headers.get("Authorization", "")
            assert auth_header.startswith("Bearer "), "Authorization header should contain Bearer token"
            assert len(auth_header) > 7, "Token should have content after 'Bearer '"
        finally:
            service.close()
