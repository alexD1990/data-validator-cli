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
    Validation result for a single rule.
    Uses native-safe values to support JSON output.
    """
    warning: bool
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        # Convert any numpy values inside details to native Python
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
    Abstract base class for validation rules.
    """
    name: str = "rule"

    def apply(self, profile: Dict[str, Any]) -> ValidationResult:
        raise NotImplementedError("Rules must implement apply()")
