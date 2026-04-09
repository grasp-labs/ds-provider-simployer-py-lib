"""
**File:** ``02_dataset_read.py``
**Region:** ``examples/02_dataset_read``

Example 02: Read data from Simployer using a dataset.

This example demonstrates how to:
- Create a Simployer linked service and connect
- Create a Simployer dataset for a specific data product
- Read employee data from the Simployer API
- Handle pagination and checkpointing

Prerequisites:
    Set environment variables or provide credentials directly:
    - SIMPLOYER_CLIENT_ID: Your Simployer client ID
    - SIMPLOYER_CLIENT_SECRET: Your Simployer client secret
"""

from __future__ import annotations

import logging
import os
from uuid import uuid4

from ds_common_logger_py_lib import Logger

from ds_provider_simployer_py_lib.dataset.simployer import (
    ReadSettings,
    SimployerDataset,
    SimployerDatasetSettings,
)
from ds_provider_simployer_py_lib.enums import SimployerDataProducts
from ds_provider_simployer_py_lib.linked_service.simployer import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)

Logger.configure(level=logging.DEBUG)
logger = Logger.get_logger(__name__)


def main() -> None:
    """Main function demonstrating Simployer dataset read operations."""
    # Get credentials from environment or use defaults
    client_id = os.getenv("SIMPLOYER_CLIENT_ID", "your_client_id")
    client_secret = os.getenv("SIMPLOYER_CLIENT_SECRET", "your_client_secret")

    # Create Simployer linked service settings
    linked_service_settings = SimployerLinkedServiceSettings(
        client_id=client_id,
        client_secret=client_secret,
    )

    # Create the linked service
    linked_service = SimployerLinkedService(
        settings=linked_service_settings,
        id=str(uuid4()),
        name="Simployer Linked Service",
        description="Linked service for connecting to Simployer API",
        version="1.0",
    )

    # Create dataset settings for reading employees
    dataset_settings = SimployerDatasetSettings(
        data_product=SimployerDataProducts.EMPLOYEES,
        read=ReadSettings(
            page_size=100,  # Number of records per page
            # Optional filters:
            # from_date="2024-01-01",
            # to_date="2024-12-31",
        ),
    )

    # Create the dataset
    dataset = SimployerDataset(
        id=str(uuid4()),
        name="Simployer Employees Dataset",
        version="1.0",
        linked_service=linked_service,
        settings=dataset_settings,
    )

    try:
        # Connect to Simployer
        logger.info("Connecting to Simployer...")
        linked_service.connect()
        logger.info("✓ Connected successfully!")

        # Read data from the API
        logger.info("Reading employee data from Simployer...")
        dataset.read()

        # Access the results
        if dataset.output is not None and not dataset.output.empty:
            logger.info("✓ Read %d employees", len(dataset.output))
            logger.debug("Columns: %s", list(dataset.output.columns))
            logger.debug("First few rows:\n%s", dataset.output.head())
        else:
            logger.info("No employee data returned")

        # The checkpoint can be persisted for incremental loads
        if dataset.supports_checkpoint and dataset.checkpoint:
            logger.debug("Checkpoint for next run: %s", dataset.checkpoint)

    except Exception as exc:
        logger.error("Failed to read data: %s", exc)
        raise

    finally:
        # Clean up
        linked_service.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    main()
