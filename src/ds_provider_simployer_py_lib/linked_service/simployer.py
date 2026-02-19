"""
**File:** ``simployer.py``
**Region:** ``ds_provider_simployer_py_lib/linked_service/simployer``

Simployer Linked Service

This module implements a linked service for Simployer, allowing users to connect to and interact with
Simployer instance using client credentials.

Example:
    >>> from uuid import uuid4
    >>> linked_service = SimployerLinkedService(
    ...     settings=SimployerLinkedServiceSettings(
    ...         client_id="your_client_id",
    ...         client_secret="your_client_secret",
    ...     ),
    ...     id=uuid4(),
    ...     name="simployer-connection",
    ...     version="1.0.0",
    ...     description="Simployer API connection"
    ... )
    >>> # For testing credentials
    >>> success, message = linked_service.test_connection()
    >>> # For actual usage with persistent connection
    >>> linked_service.connect()
    >>> try:
    ...     session = linked_service.session  # Use session for API calls
    ... finally:
    ...     linked_service.close()
"""

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from ds_common_logger_py_lib import Logger
from ds_protocol_http_py_lib import HttpLinkedService, HttpLinkedServiceSettings, enums
from ds_protocol_http_py_lib.linked_service import CustomAuthSettings

from ..enums import ResourceType

logger = Logger.get_logger(__name__, package=True)

# -------------------------------
# settings class
# -------------------------------


@dataclass(kw_only=True)
class SimployerLinkedServiceSettings(HttpLinkedServiceSettings):
    """
    Settings required to connect to Simployer API using client credentials.

    Attributes:
        client_id: Client ID for authentication
        client_secret: Client secret for authentication
        token_endpoint: Token endpoint (default: https://simplauth.simployer.com/oauth/token)
        audience: Audience identifier (default: https://hrconnect.simployer.com)
        api_version: API version to use (default: v1)
        host: API host URL (default: https://hrconnect.simployer.com)
        auth_type: Authentication type (default: CUSTOM)
        custom: Custom authentication settings, required if auth_type is CUSTOM
    """

    client_id: str
    """The client ID for authentication."""

    client_secret: str = field(repr=False, metadata={"mask": True})
    """The client secret for authentication."""

    token_endpoint: str = "https://simplauth.simployer.com/oauth/token"
    """The token endpoint URL."""

    audience: str = "https://hrconnect.simployer.com"
    """The audience identifier."""

    api_version: str = "v1"
    """The API version to use."""

    host: str = "https://hrconnect.simployer.com"
    """The API host URL."""

    auth_type: enums.AuthType = enums.AuthType.CUSTOM
    """The authentication type to use."""

    custom: CustomAuthSettings | None = None
    """Custom authentication settings, required if auth_type is CUSTOM."""


SimployerLinkedServiceSettingsType = TypeVar(
    "SimployerLinkedServiceSettingsType",
    bound="SimployerLinkedServiceSettings",
)

# -------------------------------
# LinkedService class
# -------------------------------


@dataclass(kw_only=True)
class SimployerLinkedService(
    HttpLinkedService[SimployerLinkedServiceSettingsType],
    Generic[SimployerLinkedServiceSettingsType],
):
    """
    Linked service for connecting to Simployer using client credentials.

    """

    settings: SimployerLinkedServiceSettingsType

    @property
    def type(self) -> ResourceType:  # type: ignore[override]
        """
        Get the type of the linked service.

        Returns:
             ResourceType
        """
        return ResourceType.SIMPLOYER_LINKED_SERVICE

    def __post_init__(self) -> None:
        """
        Post-init method to set up the linked service.

        Returns:
            None
        """
        super().__post_init__()
        self.settings.custom = CustomAuthSettings(
            token_endpoint=self.settings.token_endpoint,
            data={
                "client_id": self.settings.client_id,
                "client_secret": self.settings.client_secret,
                "audience": self.settings.audience,
                "grant_type": "client_credentials",
            },
        )
