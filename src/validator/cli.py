import os

import typer
from rich.console import Console

from validator.profiler import quick_profile
from validator.engine import RuleEngine
from validator.renderers import (
    render_summary,
    render_structural,
    render_quality,
    render_numeric,
    render_status,
)
from validator.rules.structural import NonEmptyRule, DuplicateRule
from validator.rules.quality import NullRatioRule, TypeMismatchRule, WhitespaceRule
from validator.rules.numeric import NumericOutlierRule

app = typer.Typer(help="Simple and fast data validation CLI utility.")
console = Console()


@app.command()
def validate(
    path: str,
    summary: bool = typer.Option(False, "--summary", help="Only show summary."),  # reserved for later
    json_output: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """
    CLI entrypoint for validating a dataset.

    Flow:
    - Load dataset using profiling module
    - Execute validation rules
    - Render console output or JSON
    """
    console.print(f"[bold]Reading:[/bold] {path}")

    # Structural fail: empty file
    if os.path.getsize(path) == 0:
        msg = "Validation error: file is empty"
        if json_output:
            console.print(f"[red]{msg}[/red]")
        else:
            console.print(f"[bold red] {msg}[/bold red]")
        raise typer.Exit(code=2)

    # Read + profile
    try:
        profile = quick_profile(path)
    except Exception as e:
        msg = f"Error reading file: {e}"
        if json_output:
            console.print(f"[red]{msg}[/red]")
        else:
            console.print(f"[red] {msg}[/red]")
        raise typer.Exit(code=2)

    # RuleEngine setup
    engine = RuleEngine(
        structural_rules=[
            NonEmptyRule(),
            DuplicateRule(),
        ],
        quality_rules=[
            NullRatioRule(),
            TypeMismatchRule(),
            WhitespaceRule(),
        ],
        numeric_rules=[
            NumericOutlierRule(),
        ],
    )

    report = engine.run(profile)

    # JSON mode
    if json_output:
        # Exit code: 0 if no warnings, 1 if warnings, 2 already used for structural fail
        print(report.to_json())
        raise typer.Exit(code=0 if not report.has_warnings else 1)

    # Console mode (existing behavior preserved)
    render_summary(report)
    render_structural(report.structural_results)
    render_quality(report.quality_results)
    render_numeric(report)
    render_status(report)

    # In console mode, keep exit code 0 even with warnings (backward compatible)
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
