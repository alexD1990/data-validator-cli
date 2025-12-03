import pytest
import pandas as pd
from pathlib import Path

from dfguard.profiler import profile_dataframe, quick_profile


class TestProfiler:

    def test_profile_dataframe_basic(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        profile = profile_dataframe(df)

        assert "df" in profile
        assert "rows" in profile
        assert profile["rows"] == 3

    def test_profile_dataframe_empty(self):
        df = pd.DataFrame()
        profile = profile_dataframe(df)

        assert profile["rows"] == 0
        assert isinstance(profile["df"], pd.DataFrame)

    def test_quick_profile_csv(self, tmp_path):
        df = pd.DataFrame({"x": [1, 2, 3]})
        p = tmp_path / "test.csv"
        df.to_csv(p, index=False)

        profile = quick_profile(str(p))
        assert profile["rows"] == 3
        assert "df" in profile
        assert isinstance(profile["df"], pd.DataFrame)

    def test_quick_profile_parquet(self, tmp_path):
        df = pd.DataFrame({"x": [1, 2, 3]})
        p = tmp_path / "test.parquet"
        df.to_parquet(p, index=False)

        profile = quick_profile(str(p))
        assert profile["rows"] == 3

    def test_quick_profile_missing_file(self, tmp_path):
        """quick_profile() should raise a clear error when file not found."""
        missing = tmp_path / "nope.csv"
        with pytest.raises(Exception):
            quick_profile(str(missing))

    def test_quick_profile_detects_whitespace(self, tmp_path):
        df = pd.DataFrame({"name": [" a", "b "]})
        p = tmp_path / "ws.csv"
        df.to_csv(p, index=False)

        profile = quick_profile(str(p))

        # Data should not get mangled
        assert profile["df"].iloc[0]["name"] == " a"
        assert profile["rows"] == 2
