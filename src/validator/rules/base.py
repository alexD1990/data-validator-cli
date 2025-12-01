from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ValidationResult:
    """
    Normalized validation output contract (v1.0a.1).

    message: str
        Short fact-based label describing the type of check,
        e.g. "Duplicate rows", "Null ratio", "Type consistency".

    warning: bool
        True if rule considers the condition problematic.

    details: dict
        MUST contain raw numeric values only.
        Renderer decides formatting.
        
        Example for structural rule:
        {
            "count": 12,
            "ratio": 0.045,            # float
            "total_rows": 267          # int
        }

        Example for multiple-column rules:
        {
            "columns": {
                "price": {"count": 12, "ratio": 0.012},
                "quantity": {"count": 3, "ratio": 0.003}
            }
        }
    """
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
