class NumericOutlierRule(BaseRule):
    name = "numeric_outliers"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        numeric_cols = df.select_dtypes(include=["number"]).columns

        details = {"columns": {}}

        for col in numeric_cols:
            s = df[col].dropna()
            if s.empty:
                continue

            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            mask = (s < lower) | (s > upper)
            count = int(mask.sum())

            details["columns"][col] = {
                "count": count,
                "ratio": float(count / len(s)) if len(s) else 0.0,
            }

        warning = any(
            col_info["count"] > 0
            for col_info in details["columns"].values()
        )

        return ValidationResult(
            warning=warning,
            message="Numeric outliers",
            details=details,
        )

