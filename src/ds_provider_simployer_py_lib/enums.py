"""
**File:** ``enums.py``
**Region:** ``ds_provider_simployer_py_lib/enums``

Constants for Simployer provider.

Example:
    >>> ResourceType.LINKED_SERVICE
    'ds.resource.linked-service.simployer'
"""

from enum import StrEnum


class ResourceType(StrEnum):
    """
    Constants for Simployer provider.
    """

    SIMPLOYER_LINKED_SERVICE = "ds.resource.linked-service.simployer"
