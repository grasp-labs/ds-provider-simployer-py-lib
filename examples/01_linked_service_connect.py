"""
**File:** ``01_linked_service_connect.py``
**Region:** ``examples/01_linked_service_connect``

Example 01: Connect to Simployer using a linked service.

This example demonstrates how to:
- Create a Simployer linked service with OAuth2 client credentials
- Test the connection to Simployer
- Use the linked service for API interactions

Prerequisites:
    Set environment variables or provide credentials directly:
    - SIMPLOYER_CLIENT_ID: Your Simployer OAuth2 client ID
    - SIMPLOYER_CLIENT_SECRET: Your Simployer OAuth2 client secret
"""

from __future__ import annotations

import os
from uuid import uuid4
import logging

from ds_common_logger_py_lib import Logger

from ds_provider_simployer_py_lib.linked_service.simployer import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)

Logger.configure(level=logging.DEBUG)
logger = Logger.get_logger(__name__)


def main() -> None:
    """Main function demonstrating Simployer linked service connection."""
    # Get credentials from environment or use defaults
    client_id = os.getenv("SIMPLOYER_CLIENT_ID", "your_client_id")
    client_secret = os.getenv("SIMPLOYER_CLIENT_SECRET", "your_client_secret")

    # Create Simployer linked service settings
    settings = SimployerLinkedServiceSettings(
        client_id=client_id,
        client_secret=client_secret,
    )

    # Create the linked service
    linked_service = SimployerLinkedService(
        id=uuid4(),
        name="Simployer Linked Service",
        version="1.0.0",
        settings=settings,
    )

    try:
        logger.info("Testing connection to Simployer...")
        success, message = linked_service.test_connection()

        if success:
            logger.info("✓ Connection test successful!")
            logger.debug("Message: %s", message)
        else:
            logger.error("✗ Connection test failed: %s", message)
            return

    except ConnectionError as exc:
        logger.error("Failed to connect to Simployer: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise


if __name__ == "__main__":
    main()
