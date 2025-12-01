import os

import typer

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


@app.command()
def validate(
    path: str,
    summary: bool = typer.Option(False, "--summary", help="Only show summary."),  # behold flag for nå
    json_output: bool = typer.Option(False, "--json", help="Output as JSON."),    # v1.0b – ikke implementert ennå
):
    """
    CLI entrypoint for validating a dataset.

    Flow:
    - Load dataset using profiling module
    - Execute validation rules
    - Render structured console output
    """
    from rich.console import Console

    console = Console()
    console.print(f"[bold]Reading:[/bold] {path}")

    if os.path.getsize(path) == 0:
        console.print("[bold red] Validation error: file is empty[/bold red]")
        raise typer.Exit(code=2)

    try:
        profile = quick_profile(path)
    except Exception as e:
        console.print(f"[red] Error reading file:[/red] {e}")
        raise typer.Exit(code=2)

    # ─── RuleEngine setup ─────────────────────────────────────────────
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

    # ─── Render output ────────────────────────────────────────────────
    render_summary(profile)
    render_structural(report.structural)
    render_quality(report.quality)
    render_numeric(profile, report.numeric)
    render_status(report)

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
