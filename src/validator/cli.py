import typer
from rich.console import Console
from rich.table import Table

from validator.profiler import quick_profile
from validator.engine import RuleEngine
from validator.rules.quality import WhitespaceRule
from validator.rules.structural import NonEmptyRule
from validator.rules.quality import NullRatioRule
from validator.rules.structural import DuplicateRule
from validator.rules.quality import TypeMismatchRule
from validator.rules.numeric import NumericOutlierRule
#from validator.rules import (
   # validate_non_empty,
   # warn_high_null_ratio,
   # warn_duplicate_rows,
   # warn_general_type_mismatch,
   # warn_numeric_outliers,
   # warn_whitespace_issues,
#)

app = typer.Typer(help="Simple and fast data validation CLI utility.")
console = Console()


@app.command()
def validate(
    path: str,
    summary: bool = typer.Option(False, "--summary", help="Only show summary."),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """
    CLI entrypoint for validating a dataset.

    Flow:
    - Load dataset using profiling module
    - Execute validation rules (e.g. minimum row count)
    - Display results and exit with appropriate code
    """
    console.print(f"[bold]Reading:[/bold] {path}")

    import os
    if os.path.getsize(path) == 0:
        console.print("[bold red] Validation error: file is empty[/bold red]")
        raise typer.Exit(code=2)

    try:
        profile = quick_profile(path)
    except Exception as e:
        console.print(f"[red] Error reading file:[/red] {e}")
        raise typer.Exit(code=2)

    # ─── RuleEngine Execution ─────────────────────────────────────────────

    engine = RuleEngine(rules=[
        NonEmptyRule(),
        NullRatioRule(),
        DuplicateRule(),
        TypeMismatchRule(),
        NumericOutlierRule(),   # NEW
        WhitespaceRule(),
    ])

    results = engine.run(profile)
    engine.render_console(results)



if __name__ == "__main__":
    app()
