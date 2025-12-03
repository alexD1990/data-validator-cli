import pandas as pd
from .base import BaseRule, ValidationResult


class NonEmptyRule(BaseRule):
    name = "non_empty"

    def apply(self, profile: dict) -> ValidationResult:
        rows = profile.get("rows", 0)

        if rows == 0:
            return ValidationResult(
                warning=True,
                message="Dataset empty",
                details={"rows": 0},
            )

        # New: always return a fact result
        return ValidationResult(
            warning=False,
            message="Dataset non-empty",
            details={"rows": rows},
        )


class DuplicateRule(BaseRule):
    name = "duplicate_rows"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        dup_count = int(df.duplicated().sum())
        ratio = dup_count / rows if rows else 0.0

        return ValidationResult(
            warning=(dup_count > 0),
            message="Duplicate rows",
            details={
                "count": dup_count,
                "ratio": f"{ratio:.1%}",
                "total_rows": rows,
            },
        )

