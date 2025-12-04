# src/dfguard/spark/engine.py

from typing import Dict
from dfguard.rules.base import ValidationResult
from dfguard.report import ValidationReport
from dfguard.rules.spark.structural import SparkNonEmptyRule, SparkDuplicateRule
from dfguard.rules.spark.quality import SparkNullRatioRule, SparkTypeMismatchRule
from dfguard.rules.spark.performance import SmallFileRule


class SparkRuleEngine:
    """
    Spark-specific rule engine.
    Mirrors the pandas RuleEngine but rules are Spark-native.
    """

    def __init__(self):
        # List of Spark-specific structural rules
        self.structural_rules = [
            SparkNonEmptyRule(),
            SparkDuplicateRule(),
        ]

        # List of Spark-specific quality rules
        self.quality_rules = [
            SparkNullRatioRule(),
            SparkTypeMismatchRule(),
        ]

        # Performance rule for detecting small files
        self.performance_rules = [
            SmallFileRule(),
        ]

    def _run_bucket(self, rules, profile: Dict) -> list:
        """
        Run a list of rules and collect results.
        This handles both structural, quality, numeric, and performance rules.
        """
        results = []
        for rule in rules:
            try:
                result = rule.apply(profile)

                # If the rule returns None (no issues), continue
                if result is None:
                    results.append(None)
                    continue

                if isinstance(result, ValidationResult):
                    setattr(result, "name", getattr(rule, "name", None))
                    results.append(result)
            except Exception as e:
                # Register rule failure as a warning
                vr = ValidationResult(
                    warning=True,
                    message=f"Rule '{getattr(rule, 'name', rule.__class__.__name__)}' failed",
                    details={"error": str(e)},
                )
                setattr(vr, "name", getattr(rule, "name", None))
                results.append(vr)

        return results

    def run(self, profile: Dict) -> ValidationReport:
        """
        Run all Spark-specific rules and return a ValidationReport.
        """
        # Run structural rules (non-empty, duplicates)
        structural_results = self._run_bucket(self.structural_rules, profile)

        # Run quality rules (null ratio, type mismatch)
        quality_results = self._run_bucket(self.quality_rules, profile)

        # Run performance rule (small file detection)
        performance_results = self._run_bucket(self.performance_rules, profile)

        return ValidationReport(
            profile=profile,
            structural_results=[r for r in structural_results if r is not None],
            quality_results=[r for r in quality_results if r is not None],
            numeric_results=[],  # Can be added later
            performance_results=[r for r in performance_results if r is not None],
        )
