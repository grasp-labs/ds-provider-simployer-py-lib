"""
**File:** ``__init__.py``
**Region:** ``ds_provider_simployer_py_lib/linked_service``

Simployer Linked Service

This module implements a linked service for Simployer and provides a session.

Example:
    >>> from uuid import UUID
    >>> linked_service = SimployerLinkedService(
    ...     id=UUID("00000000-0000-0000-0000-000000000000"),
    ...     name="test-name",
    ...     version="1.0.0",
    ...     settings=SimployerLinkedServiceSettings(
    ...         client_id="your_client_id",
    ...         client_secret="your_client_secret",
    ...     ),
    ... )
    >>> linked_service.connect()
    >>> linked_service.test_connection()
"""

from .simployer import SimployerLinkedService, SimployerLinkedServiceSettings

__all__ = [
    "SimployerLinkedService",
    "SimployerLinkedServiceSettings",
]
