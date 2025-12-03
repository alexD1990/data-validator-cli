import pytest
import pandas as pd

from dfguard import validate


class TestEdgeCases:

    # ------------------------------------------------------
    # EMPTY DF
    # ------------------------------------------------------
    def test_empty_dataframe(self):
        """Empty DataFrame must trigger structural failure."""
        df = pd.DataFrame()
        report = validate(df)

        # Your NonEmptyRule returns a warning=True
        # validate() should surface this as an "error" or "warning"
        assert report.status in ("error", "warning")
        assert report.has_warnings is True

    # ------------------------------------------------------
    # SMALL DFs
    # ------------------------------------------------------
    def test_single_row(self):
        """Single row must not trigger duplicate warnings."""
        df = pd.DataFrame({"x": [1]})
        report = validate(df)

        dup_results = [r for r in report.structural_results if r.name == "duplicate_rows"]
        if dup_results:
            assert dup_results[0].details["count"] == 0

    def test_single_column(self):
        """Single column DataFrame should still validate correctly."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        report = validate(df)
        assert report.status in ("ok", "warning")

    # ------------------------------------------------------
    # ALL NULLS
    # ------------------------------------------------------
    def test_all_nulls(self):
        """A column containing only nulls must trigger high null warning."""
        df = pd.DataFrame({"x": [None, None, None]})
        report = validate(df)
        assert report.has_warnings is True

        null_rule = [r for r in report.quality_results if r.name == "null_ratio"]
        assert null_rule, "NullRatioRule should have run"
        assert null_rule[0].details["x"] == 1.0

    # ------------------------------------------------------
    # LARGE DATAFRAME STABILITY
    # ------------------------------------------------------
    def test_large_dataframe(self):
        """Large DataFrame must not crash; performance test, not correctness."""
        df = pd.DataFrame({"x": list(range(100000))})
        report = validate(df)
        assert report.status in ("ok", "warning")

    # ------------------------------------------------------
    # UNICODE HANDLING
    # ------------------------------------------------------
    def test_unicode_strings(self):
        """Unicode strings (Norwegian characters) must not break rules."""
        df = pd.DataFrame({"name": ["Ålesund", "Tromsø", "Bodø"]})
        report = validate(df)
        assert report.status in ("ok", "warning")

    # ------------------------------------------------------
    # SPECIAL CHARACTERS
    # ------------------------------------------------------
    def test_special_characters(self):
        """Special characters must not cause crashes in profiling or rules."""
        df = pd.DataFrame({"text": ["test#1", "hello@world", "a&b=3"]})
        report = validate(df)
        assert report.status in ("ok", "warning")

    # ------------------------------------------------------
    # MIXED TYPES (SHOULD NOT CRASH)
    # ------------------------------------------------------
    def test_mixed_object_types(self):
        """DataFrames with complex Python objects must not crash."""
        df = pd.DataFrame({
            "mixed": [1, "a", None, 3.14, {"x": 1}, [1, 2], True]
        })
        report = validate(df)
        # MAIN requirement: do not crash.
        assert report.status in ("ok", "warning")

    # ------------------------------------------------------
    # VERY WIDE DATAFRAMES
    # ------------------------------------------------------
    def test_wide_dataframe(self):
        """Hundreds of columns must not break or slow validation."""
        data = {f"col_{i}": [i, i+1, i+2] for i in range(300)}
        df = pd.DataFrame(data)
        report = validate(df)
        assert report.status in ("ok", "warning")
