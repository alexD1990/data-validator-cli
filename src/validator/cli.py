import typer
from rich.console import Console
from rich.table import Table

from validator.profiler import quick_profile
from validator.rules import validate_non_empty, warn_high_null_ratio, warn_duplicate_rows

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

    # ─── Validation Rules ─────────────────────────────────────────────
    validate_non_empty(profile)
    warning_detected = warn_high_null_ratio(profile, threshold=0.5) # Warning rules (non-breaking)
    dup_warning = warn_duplicate_rows(profile, threshold_ratio=0.01)
    warning_detected = warning_detected or dup_warning
    # Add more rules here later (e.g. null ratio, duplicates, etc.)
    # ─────────────────────────────────────────────────────────────────

    # ─── Display Output ───────────────────────────────────────────────
    table = Table(show_header=False, show_edge=False)
    table.add_row("Rows:", str(profile.get("rows")))
    table.add_row("Columns:", str(profile.get("columns")))

    if not summary:
        table.add_row("Column names:", ", ".join(profile.get("column_names")))
        nulls = profile.get("nulls")
        null_info = ", ".join([f"{col}: {v}" for col, v in nulls.items()])
        table.add_row("Null values:", null_info)

    console.print("\n[bold cyan]Data Validation Report[/bold cyan]")
    console.print(table)
    if warning_detected:
        console.print("[yellow] Status: WARNING[/yellow]")
    else:
        console.print("[bold green] Status: OK[/bold green]\n")

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
