from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ValidationResult:
    warning: bool
    message: str
    details: Optional[Dict] = None


class BaseRule:
    """
    Base class for all validation rules.
    Each rule must implement:
        - name: str
        - apply(profile: dict) -> ValidationResult
    """

    name: str = "base"

    def apply(self, profile: dict) -> ValidationResult:
        raise NotImplementedError("Rule must implement apply()")
