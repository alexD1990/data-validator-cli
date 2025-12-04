# src/dfguard/spark/engine.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from dfguard.rules.base import BaseRule, ValidationResult
from dfguard.report import ValidationReport


class SparkRuleEngine:
    """
    Spark-specific rule engine.
    Mirrors the pandas RuleEngine but rules are Spark-native.
    """

    def __init__(
        self,
        structural_rules: Optional[List[BaseRule]] = None,
        quality_rules: Optional[List[BaseRule]] = None,
        numeric_rules: Optional[List[BaseRule]] = None,
        performance_rules: Optional[List[BaseRule]] = None,
    ):
        self.structural_rules = structural_rules or []
        self.quality_rules = quality_rules or []
        self.numeric_rules = numeric_rules or []
        self.performance_rules = performance_rules or []

    def _run_bucket(
        self,
        rules: List[BaseRule],
        profile: Dict[str, Any],
    ) -> List[Optional[ValidationResult]]:
        results: List[Optional[ValidationResult]] = []

        for rule in rules:
            try:
                res = rule.apply(profile)

                if res is None:
                    results.append(None)
                    continue

                if isinstance(res, ValidationResult):
                    setattr(res, "name", getattr(rule, "name", None))
                    results.append(res)
                    continue

                raise TypeError(
                    f"Spark rule '{getattr(rule, 'name', rule.__class__.__name__)}' "
                    f"returned invalid result type: {type(res)}"
                )

            except Exception as exc:
                vr = ValidationResult(
                    warning=True,
                    message=f"Spark rule '{getattr(rule, 'name', rule.__class__.__name__)}' failed",
                    details={"error": str(exc)},
                )
                setattr(vr, "name", getattr(rule, "name", None))
                results.append(vr)

        return results

    def run(self, profile: Dict[str, Any]) -> ValidationReport:
        """
        Run Spark-native structural, quality, numeric, and performance rules.
        Returns a ValidationReport.
        """
        structural = self._run_bucket(self.structural_rules, profile)
        quality = self._run_bucket(self.quality_rules, profile)
        numeric = self._run_bucket(self.numeric_rules, profile)
        performance = self._run_bucket(self.performance_rules, profile)

        # For now, Spark validation returns no rules because we will add them later.
        return ValidationReport(
            profile=profile,
            structural_results=[r for r in structural if r is not None],
            quality_results=[r for r in quality if r is not None],
            numeric_results=[r for r in numeric if r is not None],
        )
