"""Unit tests for SimployerLinkedService."""

from uuid import uuid4

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


def test_post_init_configures_custom_auth():
    """Test that __post_init__ correctly configures CustomAuthSettings."""
    service = make_service()

    # Verify custom auth settings were created
    assert service.settings.custom is not None

    # Verify token endpoint
    assert service.settings.custom.token_endpoint == service.settings.token_endpoint

    # Verify OAuth2 data
    assert service.settings.custom.data["client_id"] == service.settings.client_id
    assert service.settings.custom.data["client_secret"] == service.settings.client_secret
    assert service.settings.custom.data["audience"] == service.settings.audience
    assert service.settings.custom.data["grant_type"] == "client_credentials"
