import pandas as pd
from validator.rules.base import BaseRule, ValidationResult


class NonEmptyRule(BaseRule):
    name = "non_empty"

    def apply(self, profile: dict) -> ValidationResult:
        rows = profile.get("rows", 0)

        if rows == 0:
            return ValidationResult(
                warning=True,
                message="Dataset is empty",
                details={"rows": 0},
            )

        return ValidationResult(
            warning=False,
            message="Dataset contains rows",
        )


class DuplicateRule(BaseRule):
    name = "duplicate_rows"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        if rows == 0:
            return ValidationResult(
                warning=False,
                message="No duplicate check on empty dataset",
            )

        dup_count = df.duplicated().sum()
        ratio = dup_count / rows

        threshold = 0.01

        if dup_count > 0 and ratio >= threshold:
            return ValidationResult(
                warning=True,
                message="Duplicate rows detected",
                details={
                    "count": dup_count,
                    "ratio": f"{ratio:.2%}",
                },
            )

        return ValidationResult(
            warning=False,
            message="No significant duplicate rows found",
        )
