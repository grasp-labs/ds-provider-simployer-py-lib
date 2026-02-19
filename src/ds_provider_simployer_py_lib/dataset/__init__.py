"""
**File:** ``__init__.py``
**Region:** ``ds_provider_simployer_py_lib/dataset``

Description
-----------
This module implements a dataset for Simployer APIs.

Example:
    >>> from ds_resource_plugin_py_lib.common.resource.dataset import DatasetStorageFormatType
    >>> from ds_resource_plugin_py_lib.common.serde.deserialize import PandasDeserializer
    >>> from ds_resource_plugin_py_lib.common.serde.serialize import PandasSerializer
    >>> dataset = SimployerDataset(
    ...     linked_service=SimployerLinkedService(
    ...         settings=SimployerLinkedServiceSettings(
    ...             host="https://api.example.com",
    ...             client_id="your_client_id",
    ...             client_secret="your_client_secret",
    ...         ),
    ...     ),
    ...     settings=SimployerDatasetSettings(
    ...         endpoint="/employees",
                method="GET",
    ...         params={"active": "true"},
    ...     ),
    ...     deserializer=PandasDeserializer(format=DatasetStorageFormatType.JSON),
    ...     serializer=PandasSerializer(format=DatasetStorageFormatType.JSON),
    ... )
    >>> dataset.read()
    >>> df = dataset.output
"""

from .simployer import SimployerDataset, SimployerDatasetSettings

__all__ = [
    "SimployerDataset",
    "SimployerDatasetSettings",
]
