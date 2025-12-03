import pytest
import pandas as pd
from typer.testing import CliRunner

from dfguard.cli import app


runner = CliRunner()


class TestCLI:

    def test_cli_runs_on_csv(self, tmp_path):
        df = pd.DataFrame({"x": [1, 2, 3]})
        p = tmp_path / "test.csv"
        df.to_csv(p, index=False)

        result = runner.invoke(app, [str(p)])
        assert result.exit_code == 0
        assert "Rows:" in result.stdout or "rows" in result.stdout.lower()

    def test_cli_json_output(self, tmp_path):
        df = pd.DataFrame({"x": [1, None, None]})
        p = tmp_path / "nulls.csv"
        df.to_csv(p, index=False)

        result = runner.invoke(app, [str(p), "--json"])
        assert result.exit_code == 0
        assert "validator_version" in result.stdout
        assert '"status"' in result.stdout

    def test_cli_missing_file(self):
        result = runner.invoke(app, ["missing.csv"])
        assert result.exit_code != 0

    def test_cli_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.stdout or "usage" in result.stdout.lower()

    def test_cli_parquet(self, tmp_path):
        df = pd.DataFrame({"x": [1, 2, 3]})
        p = tmp_path / "test.parquet"
        df.to_parquet(p, index=False)

        result = runner.invoke(app, [str(p)])
        assert result.exit_code == 0

    def test_cli_always_shows_all_sections(tmp_path):
    # minimal dataset
    df = pd.DataFrame({"x": [1]})
    path = tmp_path / "one.csv"
    df.to_csv(path, index=False)

    result = runner.invoke(app, [str(path)])

    out = result.stdout

    assert "Data Summary" in out
    assert "Structural" in out
    assert "Quality" in out
    assert "Numeric Distribution" in out
    assert "Status:" in out

    def test_cli_warning_symbol(tmp_path):
    df = pd.DataFrame({"x": [1, 1000]})
    path = tmp_path / "warn.csv"
    df.to_csv(path, index=False)

    out = runner.invoke(app, [str(path)]).stdout

    assert "⚠" in out
    assert "Status: WARNING" in out
