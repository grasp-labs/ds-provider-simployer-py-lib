"""
**File:** ``simployer.py``
**Region:** ``ds_provider_simployer_py_lib/linked_service/simployer``

Simployer Linked Service

This module implements a linked service for Simployer, allowing users to connect to and interact with
Simployer instance using OAuth2 client credentials.

Example:
    >>> from uuid import uuid4
    >>> linked_service = SimployerLinkedService(
    ...     settings=SimployerLinkedServiceSettings(
    ...         auth_type="OAUTH2",
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

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import requests
from ds_common_logger_py_lib import Logger
from ds_protocol_http_py_lib import HttpLinkedServiceSettings, enums
from ds_resource_plugin_py_lib.common.resource.linked_service import LinkedService

from ..enums import ResourceType

logger = Logger.get_logger(__name__, package=True)

# -------------------------------
# Settings class
# -------------------------------


@dataclass(kw_only=True)
class SimployerLinkedServiceSettings(HttpLinkedServiceSettings):
    """
    Settings required to connect to Simployer API using OAuth2 client credentials.

    Attributes:
        client_id: OAuth2 client ID for authentication
        client_secret: OAuth2 client secret for authentication
        auth_url: OAuth2 token endpoint (default: https://simplauth.simployer.com/oauth/token)
        audience: OAuth2 audience identifier (default: https://hrconnect.simployer.com)
        api_version: API version to use (default: v1)
        host: API host URL (default: https://hrconnect.simployer.com)
        timeout_seconds: Request timeout in seconds for API calls (default: 30)
    """

    client_id: str
    client_secret: str = field(repr=False)
    auth_url: str = "https://simplauth.simployer.com/oauth/token"
    audience: str = "https://hrconnect.simployer.com"
    api_version: str = "v1"
    host: str = "https://hrconnect.simployer.com"
    timeout_seconds: int = 30
    auth_type: enums.AuthType = enums.AuthType.OAUTH2


SimployerLinkedServiceSettingsType = TypeVar(
    "SimployerLinkedServiceSettingsType",
    bound="SimployerLinkedServiceSettings",
)

# -------------------------------
# LinkedService class
# -------------------------------


@dataclass(kw_only=True)
class SimployerLinkedService(
    LinkedService[SimployerLinkedServiceSettingsType],
    Generic[SimployerLinkedServiceSettingsType],
):
    """
    Linked service for connecting to Simployer using OAuth2 client credentials.

    """

    settings: SimployerLinkedServiceSettingsType
    _access_token: str | None = field(default=None, init=False, repr=False)
    _session: requests.Session | None = field(default=None, init=False, repr=False)

    def _validate_settings(self) -> None:
        """
        Validate that settings are configured correctly.

        Returns:
            None

        Raises:
            AttributeError: If settings are not set correctly.
        """
        if not isinstance(self.settings, SimployerLinkedServiceSettings):
            raise AttributeError("Settings not set correctly.")

    @property
    def type(self) -> ResourceType:
        """
        Get the type of the linked service.

        Returns:
             ResourceType
        """
        return ResourceType.SIMPLOYER_LINKED_SERVICE

    @property
    def session(self) -> requests.Session:
        """
        Get the authenticated requests.Session for making API calls.

        Returns:
            requests.Session: A session configured with authentication headers.

        Raises:
            ConnectionError: If not connected or session is unavailable.
        """
        if self._session is None:
            raise ConnectionError("Not connected. Call connect() first.")
        return self._session

    def connect(self) -> None:
        """
        Connect to Simployer API by validating settings and obtaining an access token.

        Returns:
            None

        Raises:
            ConnectionError: If required settings are missing or authentication fails
        """
        # Close any existing session to prevent resource leaks
        self.close()

        self._validate_settings()

        if not self.settings.client_id:
            raise ConnectionError("Client ID is missing")
        if not self.settings.client_secret:
            raise ConnectionError("Client secret is missing")
        if not self.settings.host:
            raise ConnectionError("Host URL is missing")

        # Obtain access token
        self._access_token = self._get_access_token()

        # Create authenticated session
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }
        )

        logger.debug("Simployer LinkedService connected successfully.")

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the connection to Simployer by authenticating and obtaining a token.

        This method creates a temporary connection for testing purposes. If the service
        was already connected before calling this method, the existing connection is
        preserved. If not connected, any temporary connection created during the test
        is cleaned up before returning.

        Returns:
            tuple[bool, str]: A tuple containing a boolean indicating success and a message.
        """
        was_connected = self._session is not None
        try:
            self.connect()
            return True, "Connection successfully tested"
        except ConnectionError as exc:
            return False, str(exc)
        finally:
            # Only close if we weren't already connected (i.e., this test created a temporary connection)
            if not was_connected:
                self.close()

    def close(self) -> None:
        """
        Close the connection. Clears the cached access token and session.

        Returns:
            None
        """
        if self._session:
            self._session.close()
        self._session = None
        self._access_token = None
        logger.debug("Simployer LinkedService closed.")

    def _get_access_token(self) -> str:
        """
        Obtain an OAuth2 access token using client credentials.

        Returns:
            str: The access token for API authentication.

        Raises:
            ConnectionError: If authentication fails or the response is invalid.
        """
        try:
            response = requests.post(
                self.settings.auth_url,
                data={
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                    "audience": self.settings.audience,
                    "grant_type": "client_credentials",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.settings.timeout_seconds,
            )
            response.raise_for_status()

            try:
                token_data: dict[str, Any] = response.json()
            except ValueError as exc:
                content_type = response.headers.get("Content-Type", "")
                raise ConnectionError(
                    f"Invalid authentication response: expected JSON body but received content type '{content_type or 'unknown'}'."
                ) from exc
            access_token = token_data.get("access_token")

            if not access_token:
                raise ConnectionError("Access token not found in authentication response")

            return str(access_token)

        except requests.RequestException as exc:
            raise ConnectionError(f"Failed to obtain access token: {exc}") from exc
