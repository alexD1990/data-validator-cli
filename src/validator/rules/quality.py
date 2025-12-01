import pandas as pd
from validator.rules.base import BaseRule, ValidationResult

class WhitespaceRule(BaseRule):
    name = "whitespace_issues"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)
        issues = {}

        for col in df.columns:
            s = df[col].astype(str)

            mask_strip = s.str.strip() != s
            mask_internal = s.str.contains(r"\s{2,}", regex=True)
            mask_tabs = s.str.contains("\t", regex=False) | s.str.contains(r"\\t")

            mask = mask_strip | mask_internal | mask_tabs
            affected = int(mask.sum())

            if affected > 0 and affected / rows >= 0.05:
                issues[col] = affected

        if issues:
            return ValidationResult(
                warning=True,
                message="Whitespace issues detected",
                details=issues
            )

        return ValidationResult(
            warning=False,
            message="No whitespace issues"
        )

class NullRatioRule(BaseRule):
    name = "null_ratio"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        nulls = df.isna().sum()
        rows = len(df)

        issues = {}

        # Same logic as warn_high_null_ratio(profile, threshold=0.5)
        threshold = 0.5

        for col, count in nulls.items():
            ratio = count / rows if rows > 0 else 0
            if ratio >= threshold:
                issues[col] = f"{ratio:.2%}"

        if issues:
            return ValidationResult(
                warning=True,
                message="High null ratio detected",
                details=issues
            )

        return ValidationResult(
            warning=False,
            message="Null ratio within normal bounds"
        )

class TypeMismatchRule(BaseRule):
    name = "type_mismatch"

    def apply(self, profile: dict) -> ValidationResult:
        df = profile["df"]
        rows = len(df)

        if rows == 0:
            return ValidationResult(
                warning=False,
                message="No type mismatch check on empty dataset"
            )

        issues = {}

        # Same logic as old warn_general_type_mismatch threshold_ratio=0.8
        threshold_ratio = 0.8

        for col in df.columns:
            series = df[col]

            # Only analyze object/string columns — those that can hide type noise
            if series.dtype == object or pd.api.types.is_string_dtype(series):
                coerced = pd.to_numeric(series, errors="coerce")
                valid = coerced.notna().sum()
                ratio = valid / rows

                # If less than 80% values can convert → likely type mismatch
                if ratio < threshold_ratio:
                    issues[col] = f"{ratio:.2%} convertible"

        if issues:
            return ValidationResult(
                warning=True,
                message="Potential type mismatch detected",
                details=issues
            )

        return ValidationResult(
            warning=False,
            message="No significant type mismatches detected"
        )
