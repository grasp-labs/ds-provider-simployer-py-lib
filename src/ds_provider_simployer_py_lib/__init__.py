"""
**File:** ``__init__.py``
**Region:** ``ds-provider-simployer-py-lib``

Description
-----------
A Python package from the ds-provider-simployer-py-lib library.

Example
-------
.. code-block:: python

    from ds_provider_simployer_py_lib import __version__

    print(f"Package version: {__version__}")
"""

from importlib.metadata import version

__version__ = version("ds-provider-simployer-py-lib")
__all__ = ["__version__"]
