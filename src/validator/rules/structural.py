import pandas as pd
from validator.rules.base import BaseRule, ValidationResult


class NonEmptyRule(BaseRule):
    name = "non_empty"

    def apply(self, profile: dict) -> ValidationResult:
        rows = profile.get("rows", 0)

        if rows == 0:
            return ValidationResult(
                warning=True,
                message="Dataset empty",
                details={"total_rows": 0},
            )

        # No warning, but still fact-based details
        return ValidationResult(
            warning=False,
            message="Dataset empty",
            details={"total_rows": rows},
        )


class DuplicateRule(BaseRule):
    name = "duplicate_rows"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        dup_count = int(df.duplicated().sum())
        ratio = dup_count / rows if rows else 0.0

        return ValidationResult(
            warning=(dup_count > 0),  # renderer decides significance
            message="Duplicate rows",
            details={
                "count": dup_count,
                "ratio": float(ratio),
                "total_rows": rows,
            },
        )
