"""
**File:** ``__init__.py``
**Region:** ``ds_provider_simployer_py_lib/dataset``

Description
-----------
This module implements a dataset for Simployer APIs.

Example:
    >>> from uuid import uuid4
    >>> dataset = SimployerDataset(
    ...     settings=SimployerDatasetSettings(
    ...         linked_service_id=uuid4(),
    ...         endpoint="/employees",
    ...         query_params={"active": "true"},
    ...     ),
    ...     id=uuid4(),
    ...     name="active-employees",
    ...     version="1.0.0",
    ...     description="Dataset of active employees from Simployer"
    ... )
    >>> dataset.connect()
    >>> data = dataset.read()
"""

from .simployer import SimployerDataset, SimployerDatasetSettings

__all__ = [
    "SimployerDataset",
    "SimployerDatasetSettings",
]
