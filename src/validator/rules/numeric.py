import pandas as pd
from validator.rules.base import BaseRule, ValidationResult

class NumericOutlierRule(BaseRule):
    name = "numeric_outliers"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        numeric_cols = df.select_dtypes(include=["number"]).columns

        issues = {}

        for col in numeric_cols:
            s = df[col].dropna()

            if len(s) == 0:
                continue

            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            mask = (s < lower) | (s > upper)
            outliers = int(mask.sum())

            if outliers > 0:
                issues[col] = outliers

        if issues:
            return ValidationResult(
                warning=True,
                message="Numeric outliers detected",
                details=issues
            )

        return ValidationResult(
            warning=False,
            message="No numeric outliers detected"
        )
