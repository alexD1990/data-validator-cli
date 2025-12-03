import pytest
import pandas as pd

from dfguard.profiler import profile_dataframe
from dfguard.rules.quality import (
    WhitespaceRule,
    NullRatioRule,
    TypeMismatchRule,
)
from dfguard.rules.numeric import NumericOutlierRule
from dfguard.rules.structural import NonEmptyRule, DuplicateRule


# ============================================================
#  QUALITY RULES
# ============================================================

class TestWhitespaceRule:

    def test_no_whitespace_no_warning(self):
        df = pd.DataFrame({"clean": ["a", "b", "c"]})
        profile = profile_dataframe(df)
        result = WhitespaceRule().apply(profile)
        assert result.warning is False
        assert result.details["clean"] == 0

    def test_whitespace_triggers_warning(self):
        df = pd.DataFrame({"dirty": [" a", "b ", "  c  "]})
        profile = profile_dataframe(df)
        result = WhitespaceRule().apply(profile)
        assert result.warning is True
        assert result.details["dirty"] > 0

    def test_mixed_columns_only_shows_affected(self):
        df = pd.DataFrame({
            "clean": ["a", "b"],
            "dirty": [" x", "y "]
        })
        profile = profile_dataframe(df)
        result = WhitespaceRule().apply(profile)
        assert result.warning is True
        assert result.details["dirty"] > 0
        assert result.details["clean"] == 0

    def test_zero_count_columns_excluded(self):
        df = pd.DataFrame({"col": ["a", "b", "c"]})
        profile = profile_dataframe(df)
        result = WhitespaceRule().apply(profile)
        # Rule returns all columns, but count must be 0
        assert result.details["col"] == 0
        assert result.warning is False


class TestNullRatioRule:

    def test_low_null_ratio_no_warning(self):
        df = pd.DataFrame({"x": [1, None, 3]})
        profile = profile_dataframe(df)
        result = NullRatioRule().apply(profile)
        # null ratio = 1/3 < 0.5
        assert result.warning is False

    def test_high_null_ratio_triggers_warning(self):
        df = pd.DataFrame({"x": [None, None, 1, None]})
        profile = profile_dataframe(df)
        result = NullRatioRule().apply(profile)
        assert result.warning is True
        assert result.details["x"] >= 0.5

    def test_all_nulls_warning(self):
        df = pd.DataFrame({"x": [None, None, None]})
        profile = profile_dataframe(df)
        result = NullRatioRule().apply(profile)
        assert result.warning is True
        assert result.details["x"] == 1.0


class TestTypeMismatchRule:

    def test_pure_string_column_no_warning(self):
        df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
        profile = profile_dataframe(df)
        rule = TypeMismatchRule()
        result = rule.apply(profile)
        assert result is None, "Pure string columns should not warn"

    def test_zero_mismatch_numeric_column_no_warning(self):
        df = pd.DataFrame({"value": [1, 2, 3]})
        profile = profile_dataframe(df)
        rule = TypeMismatchRule()
        result = rule.apply(profile)
        assert result is None, "Numeric columns should be ignored"

    def test_mixed_types_triggers_warning(self):
        df = pd.DataFrame({"value": [1, "two", 3]})
        profile = profile_dataframe(df)
        rule = TypeMismatchRule()
        result = rule.apply(profile)
        assert result is not None
        assert result.warning is True
        assert "value" in result.details

    def test_numeric_strings_are_convertible(self):
        df = pd.DataFrame({"value": ["1", "2", "3"]})
        profile = profile_dataframe(df)
        rule = TypeMismatchRule()
        result = rule.apply(profile)
        assert result is None, "Pure numeric-string columns should NOT warn"


# ============================================================
#  NUMERIC RULES
# ============================================================

class TestNumericOutlierRule:

    def test_no_outliers(self):
        df = pd.DataFrame({"value": [10, 11, 12, 13]})
        profile = profile_dataframe(df)
        result = NumericOutlierRule().apply(profile)
        assert result.warning is False
        assert result.details["columns"]["value"]["count"] == 0

    def test_detects_outliers(self):
        df = pd.DataFrame({"value": [10, 12, 11, 9999]})
        profile = profile_dataframe(df)
        result = NumericOutlierRule().apply(profile)
        assert result.warning is True
        assert result.details["columns"]["value"]["count"] == 1

    def test_empty_numeric_column(self):
        df = pd.DataFrame({"value": [None, None]})
        profile = profile_dataframe(df)
        result = NumericOutlierRule().apply(profile)
        # no numeric values → no outliers
        assert result.warning is False


# ============================================================
#  STRUCTURAL RULES
# ============================================================

class TestNonEmptyRule:

    def test_empty_dataframe_triggers_warning(self):
        df = pd.DataFrame()
        profile = profile_dataframe(df)
        result = NonEmptyRule().apply(profile)
        assert result is not None
        assert result.warning is True
        assert result.details["rows"] == 0

    def test_non_empty_returns_none(self):
        df = pd.DataFrame({"x": [1]})
        profile = profile_dataframe(df)
        result = NonEmptyRule().apply(profile)
        assert result is None


class TestDuplicateRule:

    def test_no_duplicates(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        profile = profile_dataframe(df)
        result = DuplicateRule().apply(profile)
        assert result.warning is False
        assert result.details["count"] == 0
        assert result.details["ratio"] == 0.0

    def test_detects_duplicates(self):
        df = pd.DataFrame({"x": [1, 1, 2]})
        profile = profile_dataframe(df)
        result = DuplicateRule().apply(profile)
        assert result.warning is True
        assert result.details["count"] == 1
        assert result.details["ratio"] > 0

    def test_all_duplicates(self):
        df = pd.DataFrame({"x": [1, 1, 1, 1]})
        profile = profile_dataframe(df)
        result = DuplicateRule().apply(profile)
        assert result.warning is True
        assert result.details["count"] == 3
        assert result.details["ratio"] == 3 / 4
