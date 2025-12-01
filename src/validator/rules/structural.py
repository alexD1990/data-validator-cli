import pandas as pd
from validator.rules.base import BaseRule, ValidationResult
from typing import Optional

class NonEmptyRule(BaseRule):
    name = "non_empty"

    def apply(self, profile: dict) -> Optional[ValidationResult]:
        rows = profile.get("rows", 0)

        # FAIL CASE – dataset is empty
        if rows == 0:
            return ValidationResult(
                warning=True,
                message="Dataset empty",
                details={"rows": 0}
            )

        # OK CASE – do NOT return anything
        return None

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
