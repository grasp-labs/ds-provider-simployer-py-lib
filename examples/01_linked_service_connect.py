"""
**File:** ``01_linked_service_connect.py``
**Region:** ``examples/01_linked_service_connect``

Example 01: Connect to Simployer using a linked service.

This example demonstrates how to:
- Create a Simployer linked service
- Creates a connection using OAuth2 client credentials
- Test the connection
"""

from __future__ import annotations

from ds_common_logger_py_lib import Logger
from ds_resource_plugin_py_lib.common.resource.errors import ResourceException

from ds_provider_simployer_py_lib.linked_service.simployer import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)

logger = Logger.get_logger(__name__, package=True)


def main() -> None:
    """Main function demonstrating Simployer linked service connection."""
    linked_service = SimployerLinkedService(
        id="simployer_linked_service",
        name="Simployer Linked Service",
        version="1.0",
        settings=SimployerLinkedServiceSettings(
            auth_type="oauth2",
            host="https://api.simployer.com",
            client_id="your_client_id",
            client_secret="your_client_secret",
        ),
    )

    try:
        logger.debug("Connecting to Simployer...")
        linked_service.connect()

        logger.debug("Testing connection...")
        success, message = linked_service.test_connection()
        if success:
            logger.debug("Connection test successful: %s", message)
        else:
            raise ResourceException(message=message)
    except ResourceException as exc:
        logger.error("Failed to connect to Simployer: %s", exc.message)
        raise
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise


if __name__ == "__main__":
    main()
