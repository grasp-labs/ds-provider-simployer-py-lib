"""
**File:** ``__init__.py``
**Region:** ``ds_provider_simployer_py_lib/dataset``

Description
-----------
This module implements a dataset for Simployer APIs, focusing on Simployer-specific
data products and parameters rather than generic HTTP concerns.

Includes custom serializers/deserializers tailored to Simployer's API contract.


"""

from .simployer import SimployerDataset, SimployerDatasetSettings

__all__ = ["SimployerDataset", "SimployerDatasetSettings"]
