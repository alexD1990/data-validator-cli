# src/dfguard/engine.py

from __future__ import annotations

from typing import List, Optional, Dict, Any

from .rules.base import BaseRule, ValidationResult
from .report import ValidationReport


class RuleEngine:
    """
    Simple rule engine that runs structural, quality, and numeric rules
    and always returns a ValidationReport.
    """

    def __init__(
        self,
        structural_rules: Optional[List[BaseRule]] = None,
        quality_rules: Optional[List[BaseRule]] = None,
        numeric_rules: Optional[List[BaseRule]] = None,
    ):
        self.structural_rules: List[BaseRule] = structural_rules or []
        self.quality_rules: List[BaseRule] = quality_rules or []
        self.numeric_rules: List[BaseRule] = numeric_rules or []

    def _run_bucket(
        self,
        rules: List[BaseRule],
        profile: Dict[str, Any],
    ) -> List[Optional[ValidationResult]]:
        """
        Apply all rules in a category. Returns a list where items may be:
        - ValidationResult if the rule fires
        - None if the rule returns clean
        Any rule failure becomes a ValidationResult(warning=True).
        """
        results: List[Optional[ValidationResult]] = []

        for rule in rules:
            try:
                result = rule.apply(profile)

                # Clean path → rule returns None
                if result is None:
                    results.append(None)
                    continue

                # Must be ValidationResult
                if isinstance(result, ValidationResult):
                    # Attach rule name so tests can find it
                    setattr(result, "name", getattr(rule, "name", None))
                    results.append(result)
                    continue

                # Invalid return type
                raise TypeError(
                    f"Rule '{getattr(rule, 'name', rule.__class__.__name__)}' "
                    f"returned invalid result type: {type(result)}"
                )

            except Exception as exc:
                # Register rule failure as a warning
                vr = ValidationResult(
                    warning=True,
                    message=f"Rule '{getattr(rule, 'name', rule.__class__.__name__)}' failed",
                    details={"error": str(exc)},
                )
                setattr(vr, "name", getattr(rule, "name", None))
                results.append(vr)

        return results

    def run(self, profile: Dict[str, Any]) -> ValidationReport:
        """
        Run all rule buckets and return a unified ValidationReport.
        This is the ONLY place that constructs ValidationReport.
        """
        structural_results = self._run_bucket(self.structural_rules, profile)
        quality_results = self._run_bucket(self.quality_rules, profile)
        numeric_results = self._run_bucket(self.numeric_rules, profile)

        return ValidationReport(
            profile=profile,
            structural_results=[r for r in structural_results if r is not None],
            quality_results=[r for r in quality_results if r is not None],
            numeric_results=[r for r in numeric_results if r is not None],
        )
