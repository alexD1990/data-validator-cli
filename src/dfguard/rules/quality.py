import pandas as pd
from .base import BaseRule, ValidationResult


class WhitespaceRule(BaseRule):
    name = "whitespace_issues"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]

        details = {}
        for col in df.columns:
            s = df[col].astype(str)
            mask = (
                (s.str.strip() != s) |
                s.str.contains(r"\s{2,}") |
                s.str.contains("\t") |
                s.str.contains(r"\\t")
            )
            details[col] = int(mask.sum())

        warning = any(v > 0 for v in details.values())

        return ValidationResult(
            warning=warning,
            message="Whitespace issues",
            details=details,
        )


class NullRatioRule(BaseRule):
    name = "null_ratio"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        details = {}
        for col in df.columns:
            count = df[col].isna().sum()
            ratio = (count / rows) if rows else 0.0
            details[col] = f"{ratio:.1%}"

        warning = any((float(v.strip('%')) / 100) >= 0.5 for v in details.values())

        return ValidationResult(
            warning=warning,
            message="Null ratio",
            details=details,
        )


class TypeMismatchRule(BaseRule):
    name = "type_consistency"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        issues = {}

        for col in df.columns:
            s = df[col]

            if pd.api.types.is_numeric_dtype(s.dtype):
                continue

            coerced = pd.to_numeric(s, errors="coerce")
            numeric_count = coerced.notna().sum()

            if numeric_count == 0:
                issues[col] = "0.0%"
                continue

            if numeric_count == rows:
                issues[col] = "0.0%"  # pure numeric strings
                continue

            ratio = numeric_count / rows
            issues[col] = f"{ratio:.1%}"

        warning = any(v != "0.0%" for v in issues.values())

        return ValidationResult(
            warning=warning,
            message="Type mismatch",
            details=issues,
        )
