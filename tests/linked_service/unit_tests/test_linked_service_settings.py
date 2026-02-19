"""
**File:** ``test_linked_service_settings.py``
**Region:** ``tests/linked_service/unit_tests``

Description
-----------
SimployerLinkedService settings and initialization tests.

Covers:
- Linked service type.
- Session / client access before connection.
- Settings initialization and default values.
"""

from uuid import uuid4

from ds_provider_simployer_py_lib.linked_service import SimployerLinkedService, SimployerLinkedServiceSettings


def test_settings_defaults():
    """It initializes SimployerLinkedServiceSettings with required values and checks default values."""
    settings = SimployerLinkedServiceSettings(client_id="id", client_secret="secret", host="https://example.com")
    assert settings.token_endpoint == "https://simplauth.simployer.com/oauth/token"
    assert settings.audience == "https://hrconnect.simployer.com"
    assert settings.api_version == "v1"
    assert settings.host == "https://example.com"
    assert hasattr(settings, "auth_type")


def test_linked_service_type_property():
    """
    It exposes Simployer linked service type and settings values.
    """
    settings = SimployerLinkedServiceSettings(client_id="id", client_secret="secret", host="https://example.com")
    service = SimployerLinkedService(settings=settings, id=uuid4(), name="test", version="1.0.0", description="desc")
    assert service.type.name == "SIMPLOYER_LINKED_SERVICE"
    assert service.settings.client_id == "id"
    assert service.settings.host == "https://example.com"
