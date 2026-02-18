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

from uuid import uuid4

from ds_common_logger_py_lib import Logger

from ds_provider_simployer_py_lib.linked_service.simployer import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)

logger = Logger.get_logger(__name__, package=False)


def main() -> None:
    """Main function demonstrating Simployer linked service connection."""
    linked_service = SimployerLinkedService(
        id=uuid4(),
        name="Simployer Linked Service",
        version="1.0.0",
        settings=SimployerLinkedServiceSettings(
            auth_type="OAUTH2",
            host="https://hrconnect.simployer.com",
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
            logger.error("Connection test failed: %s", message)
    except ConnectionError as exc:
        logger.error("Failed to connect to Simployer: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise
    finally:
        linked_service.close()


if __name__ == "__main__":
    main()
