"""
**File:** ``02_dataset_read_employees.py``
**Region:** ``examples/02_dataset_read_employees``

Example 02: Read employee data from Simployer using the dataset provider.

This example demonstrates how to:
- Create a Simployer linked service with client credentials
- Configure and use a Simployer dataset to read employee data
- Perform full load (first read)
- Perform incremental load using checkpoints (resume from last position)
- Handle pagination automatically
- Use date filters and custom filters
- Access the output DataFrame
- Inspect operation details (timing, row count, schema)

Prerequisites:
    Set environment variables with your Simployer credentials:
    - SIMPLOYER_CLIENT_ID: Your Simployer API client ID
    - SIMPLOYER_CLIENT_SECRET: Your Simployer API client secret

    Or replace the os.getenv() calls with your actual credentials.

Example Usage:
    # Full load (read all employees):
    >>> python 02_dataset_read_employees.py --full

    # Incremental load (resume from checkpoint):
    >>> python 02_dataset_read_employees.py --incremental

    # With date filter:
    >>> python 02_dataset_read_employees.py --from-date 2024-01-01 --to-date 2024-12-31
"""

import json
import logging
import os
import uuid

from ds_common_logger_py_lib import Logger
from ds_resource_plugin_py_lib.common.resource.dataset.errors import ReadError

from ds_provider_simployer_py_lib.dataset.simployer import (
    SimployerDataset,
    SimployerDatasetSettings,
    ReadSettings,
)
from ds_provider_simployer_py_lib.enums import SimployerDataProducts
from ds_provider_simployer_py_lib.linked_service.simployer import (
    SimployerLinkedService,
    SimployerLinkedServiceSettings,
)

Logger.configure(level=logging.INFO)
logger = Logger.get_logger(__name__)


# 1. Create linked service (connection configuration)
linked_service = SimployerLinkedService(
    settings=SimployerLinkedServiceSettings(
        host="https://api.simployer.com",
        client_id=os.getenv("SIMPLOYER_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv("SIMPLOYER_CLIENT_SECRET", "your_client_secret"),
    ),
    id=uuid.uuid4(),
    name="Simployer API Connection",
    version="1.0.0",
)
# 2. Create dataset (what data to read)
dataset = SimployerDataset(
    settings=SimployerDatasetSettings(
        data_product=SimployerDataProducts.EMPLOYEES,
        read=ReadSettings(
            page=1,
            page_size=100,
            from_date="2024-01-01",
            to_date="2024-12-31",
            filters={"status": "active"},
    ),
    ),
    linked_service=linked_service,
    id=uuid.uuid4(),
    name="Simployer Employees Dataset",
    version="1.0.0",
)
# 3. Read data
try:
    dataset.linked_service.connect()  # Establish connection (optional, can also rely on lazy connection)
    dataset.read()
    # 4. Access output
    df = dataset.output
    print(df.head())
except ReadError as e:
    logger.error(f"Failed to read dataset: {e}")
