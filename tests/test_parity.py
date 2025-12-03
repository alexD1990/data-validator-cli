import pytest
import pandas as pd
from pathlib import Path

from dfguard import validate
from dfguard.profiler import quick_profile


class TestCLIAPIParity:

    def test_same_dataframe_same_result(self, tmp_path):
        """CLI-loaded and API-loaded DataFrames must validate identically."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "value": [10, 20, 30]
        })

        file_path = tmp_path / "test.csv"
        df.to_csv(file_path, index=False)

        # API path
        api_report = validate(df)

        # CLI path simulation
        profile = quick_profile(str(file_path))
        cli_df = profile["df"]
        cli_report = validate(cli_df)

        # Compare overall result semantics
        assert api_report.status == cli_report.status
        assert api_report.has_warnings == cli_report.has_warnings

        # Compare number of rule results
        assert len(api_report.all_results) == len(cli_report.all_results)

    def test_csv_and_parquet_equivalence(self, tmp_path):
        """CSV and Parquet versions of the same data must validate identically."""
        df = pd.DataFrame({
            "x": [1, 2, 3],
            "y": ["a", "b", "c"],
        })

        csv_path = tmp_path / "data.csv"
        parquet_path = tmp_path / "data.parquet"

        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)

        csv_profile = quick_profile(str(csv_path))
        parquet_profile = quick_profile(str(parquet_path))

        csv_report = validate(csv_profile["df"])
        parquet_report = validate(parquet_profile["df"])

        # Behavior must match exactly
        assert csv_report.status == parquet_report.status
        assert csv_report.has_warnings == parquet_report.has_warnings
        assert len(csv_report.all_results) == len(parquet_report.all_results)

    def test_round_trip_equality(self, tmp_path):
        """Saving → loading → validating must preserve rule results."""
        df_original = pd.DataFrame({
            "name": ["A", "B", "C"],
            "value": [1, 2, 3]
        })

        p = tmp_path / "roundtrip.csv"
        df_original.to_csv(p, index=False)

        profile = quick_profile(str(p))
        df_loaded = profile["df"]

        report_original = validate(df_original)
        report_loaded = validate(df_loaded)

        assert report_original.status == report_loaded.status
        assert report_original.has_warnings == report_loaded.has_warnings
