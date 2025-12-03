# src/dfguard/rules/base.py

from dataclasses import dataclass
from typing import Dict, Optional, Any
import numpy as np


def _to_native(value):
    """Convert numpy types to Python-native JSON-serializable types."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    return value


@dataclass
class ValidationResult:
    """
    Uniform container for rule results.
    """
    warning: bool
    message: str
    details: Optional[Dict[str, Any]] = None

    # NOTE:
    # A 'name' attribute will be attached dynamically by the RuleEngine.
    # As long as this class does NOT use __slots__, this works.
    #
    # Example:
    #   res = ValidationResult(...)
    #   res.name = rule.name

    def to_dict(self) -> Dict[str, Any]:
        native_details = {
            k: _to_native(v)
            for k, v in (self.details or {}).items()
        }
        return {
            "warning": self.warning,
            "message": self.message,
            "details": native_details,
        }


class BaseRule:
    """
    Abstract rule interface.
    Concrete rules must implement apply().
    """
    name: str = "rule"

    def apply(self, profile: Dict[str, Any]) -> Optional[ValidationResult]:
        raise NotImplementedError("Rules must implement apply()")
