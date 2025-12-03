from .base import BaseRule, ValidationResult
import pandas as pd


class NumericOutlierRule(BaseRule):
    name = "numeric_outliers"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        numeric_cols = df.select_dtypes(include=["number"]).columns

        result = {}

        for col in numeric_cols:
            s = df[col].dropna()
            if s.empty:
                result[col] = {"count": 0, "ratio": "0.0%"}
                continue

            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            mask = (s < lower) | (s > upper)
            count = int(mask.sum())
            ratio = count / len(s)

            result[col] = {
                "count": count,
                "ratio": f"{ratio:.1%}",
            }

        warning = any(info["count"] > 0 for info in result.values())

        return ValidationResult(
            warning=warning,
            message="Numeric outliers",
            details=result,
        )
