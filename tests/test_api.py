import pytest
import pandas as pd

from dfguard import validate


class TestValidateAPI:

    def test_clean_dataframe_returns_ok(self):
        """A clean DataFrame should result in status='ok' and no warnings."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"]
        })
        report = validate(df)

        # Must not produce any warnings
        assert report.status == "ok"
        assert report.has_warnings is False

    def test_problematic_dataframe_returns_warning(self):
        """High null ratio should produce warning."""
        df = pd.DataFrame({
            "value": [1, None, None, None]
        })
        report = validate(df)

        assert report.status == "warning"
        assert report.has_warnings is True

    def test_report_structure(self):
        """The report object must expose expected fields."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        report = validate(df)

        assert hasattr(report, "structural_results")
        assert hasattr(report, "quality_results")
        assert hasattr(report, "numeric_results")
        assert hasattr(report, "status")
        assert hasattr(report, "has_warnings")
        assert hasattr(report, "all_results")

    def test_json_serialization(self):
        """Report.to_json() must produce valid JSON."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        report = validate(df)
        json_str = report.to_json()

        assert isinstance(json_str, str)
        assert "validator_version" in json_str
        assert "status" in json_str
        assert "results" in json_str

    def test_multiple_columns_combined_rules(self):
        """Ensure validate() aggregates mixed clean/problematic columns."""
        df = pd.DataFrame({
            "good": [1, 2, 3],
            "bad": [None, None, 5],  # null_ratio = 2/3 > 0.5 → warning
        })
        report = validate(df)

        assert report.status == "warning"
        assert report.has_warnings is True
        assert any("null_ratio" in r.name for r in report.quality_results)
