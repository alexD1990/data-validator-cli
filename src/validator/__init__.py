# src/validator/__init__.py
from .version import __version__
from .core import validate  # primary Python API


__all__ = ["validate", "__version__"]