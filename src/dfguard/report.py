# src/dfguard/report.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import json

from .version import __version__
from .rules.base import ValidationResult


@dataclass
class ValidationReport:
    """
    Canonical validation report object.

    This is what validate(df) must ALWAYS return.
    """
    profile: Dict[str, Any]
    structural_results: List[Optional[ValidationResult]]
    quality_results: List[Optional[ValidationResult]]
    numeric_results: List[Optional[ValidationResult]]

    @property
    def all_results(self) -> List[ValidationResult]:
        """Flattened list of all non-None rule results."""
        return [
            r
            for r in (
                self.structural_results
                + self.quality_results
                + self.numeric_results
            )
            if r is not None
        ]

    @property
    def has_warnings(self) -> bool:
        """True if ANY rule returned warning=True."""
        return any(r.warning for r in self.all_results)

    @property
    def status(self) -> str:
        """
        Overall status:
          - "error"   if structural "empty" condition triggered
          - "warning" if any warning in any bucket
          - "ok"      otherwise
        """
        # Structural "empty" is treated as hard error
        for r in self.structural_results:
            if r is not None and r.warning:
                msg = (r.message or "").lower()
                if "empty" in msg:
                    return "error"

        if self.has_warnings:
            return "warning"

        return "ok"

    def _serialize_result(self, r: ValidationResult) -> Dict[str, Any]:
        """Convert a single ValidationResult into a JSON-serializable dict."""
        return {
            "name": getattr(r, "name", None),
            "message": r.message,
            "warning": r.warning,
            "details": r.details,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Full structured dict used by to_json()."""
        structural = [
            self._serialize_result(r)
            for r in self.structural_results
            if r is not None
        ]
        quality = [
            self._serialize_result(r)
            for r in self.quality_results
            if r is not None
        ]
        numeric = [
            self._serialize_result(r)
            for r in self.numeric_results
            if r is not None
        ]

        return {
            "validator_version": __version__,
            "file": self.profile.get("path"),
            "summary": {
                "rows": self.profile.get("rows"),
                "columns": self.profile.get("columns"),
                "types": self.profile.get("types"),
                "column_names": self.profile.get("column_names"),
            },
            "structural": structural,
            "quality": quality,
            "numeric": numeric,
            # Tests only check that "results" exists in the JSON.
            # Shape here is a nested dict of buckets.
            "results": {
                "structural": structural,
                "quality": quality,
                "numeric": numeric,
            },
            "status": self.status,
        }

    def to_json(self) -> str:
        """JSON string used by CLI --json and API clients."""
        return json.dumps(self.to_dict(), indent=2)
