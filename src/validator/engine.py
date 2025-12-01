from dataclasses import dataclass
from typing import List, Optional, Sequence, Callable

from validator.rules.base import BaseRule, ValidationResult


@dataclass
class ValidationReport:
    structural: List[ValidationResult]
    quality: List[ValidationResult]
    numeric: List[ValidationResult]


class RuleEngine:
    """
    Executes validation rules grouped by category and returns a structured report.
    Presentation/rendering is handled elsewhere.
    """

    def __init__(
        self,
        structural_rules: Optional[Sequence[BaseRule]] = None,
        quality_rules: Optional[Sequence[BaseRule]] = None,
        numeric_rules: Optional[Sequence[BaseRule]] = None,
    ) -> None:
        self.structural_rules: List[BaseRule] = list(structural_rules or [])
        self.quality_rules: List[BaseRule] = list(quality_rules or [])
        self.numeric_rules: List[BaseRule] = list(numeric_rules or [])

    def _run_bucket(self, rules: List[BaseRule], profile: dict) -> List[ValidationResult]:
        results: List[ValidationResult] = []

        for rule in rules:
            try:
                result = rule.apply(profile)
                if not isinstance(result, ValidationResult):
                    raise ValueError(
                        f"Rule {getattr(rule, 'name', rule.__class__.__name__)} "
                        f"returned invalid result type: {type(result)}"
                    )
                results.append(result)
            except Exception as e:
                # Fail-safe: a broken rule should not crash the whole validation
                results.append(
                    ValidationResult(
                        warning=True,
                        message=f"Rule '{getattr(rule, 'name', rule.__class__.__name__)}' failed: {e}",
                        details={},
                    )
                )
        return results

    def run(self, profile: dict) -> ValidationReport:
        structural_results = self._run_bucket(self.structural_rules, profile)
        quality_results = self._run_bucket(self.quality_rules, profile)
        numeric_results = self._run_bucket(self.numeric_rules, profile)

        return ValidationReport(
            structural=structural_results,
            quality=quality_results,
            numeric=numeric_results,
        )
