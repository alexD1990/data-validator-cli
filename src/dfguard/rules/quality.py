import pandas as pd
from .base import BaseRule, ValidationResult

class WhitespaceRule(BaseRule):
    name = "whitespace_issues"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        issues = {}
        for col in df.columns:
            s = df[col].astype(str)
            mask = (
                (s.str.strip() != s) |
                s.str.contains(r"\s{2,}") |
                s.str.contains("\t") |
                s.str.contains(r"\\t")
            )
            count = int(mask.sum())
            issues[col] = count

        warning = any(c > 0 for c in issues.values())

        return ValidationResult(
            warning=warning,
            message="Whitespace issues",
            details=issues,
        )

class NullRatioRule(BaseRule):
    name = "null_ratio"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        issues = {}
        for col in df.columns:
            count = df[col].isna().sum()
            ratio = count / rows if rows else 0.0
            issues[col] = float(ratio)

        # warning if ANY ratio >= 0.5 (same logic as before)
        warning = any(r >= 0.5 for r in issues.values())

        return ValidationResult(
            warning=warning,
            message="Null ratio",
            details=issues,
        )

class TypeMismatchRule(BaseRule):
    name = "type_consistency"

    def apply(self, profile: dict):
        df = profile["df"]
        rows = len(df)

        issues = {}

        for col in df.columns:
            s = df[col]

            # Skip numeric dtypes entirely
            if pd.api.types.is_numeric_dtype(s.dtype):
                continue

            # Try to convert to numeric
            coerced = pd.to_numeric(s, errors="coerce")
            numeric_count = coerced.notna().sum()

            if numeric_count == 0:
                # Pure text, OK
                continue

            if numeric_count == rows:
                # Pure numeric-strings, OK
                continue

            # Otherwise mixed → warning
            issues[col] = float(numeric_count / rows)

        if not issues:
            return None

        return ValidationResult(
            warning=True,
            message="Type mismatch",
            details=issues,
        )

