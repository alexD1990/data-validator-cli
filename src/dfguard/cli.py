# src/dfguard/cli.py

from __future__ import annotations

import sys
from pathlib import Path

import typer

from .profiler import quick_profile
from .core import validate_profile
from .renderers import render_console   

app = typer.Typer(help="DfGuard - Data validation CLI")


@app.command()
def main(
    path: str = typer.Argument(..., help="Path to CSV or Parquet file"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON instead of text"),
):
    """CLI entrypoint."""

    file_path = Path(path)

    if not file_path.exists():
        typer.echo(f"Error: file not found: {file_path}", err=True)
        raise typer.Exit(code=1)

    try:
        profile = quick_profile(str(file_path))
    except Exception as exc:
        typer.echo(f"Error: failed to read file: {exc}", err=True)
        raise typer.Exit(code=1)

    report = validate_profile(profile)

    # JSON MODE -----------------------------------------------------
    if json_output:
        typer.echo(report.to_json())
        raise typer.Exit(code=0)

    # TEXT MODE -----------------------------------------------------
    typer.echo(f"Reading: {file_path}")
    render_console(report)
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
