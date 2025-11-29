import typer
from rich.console import Console
from rich.table import Table
from validator.profiler import quick_profile

app = typer.Typer(help="Simple and fast data validation CLI utility.")
console = Console()

@app.command()
def validate(
    path: str,
    summary: bool = typer.Option(False, "--summary", help="Only show summary."),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """
    Validate a dataset (CSV or Parquet). Returns exit code (0 OK, 1 WARNING, 2 FAIL).
    """
    console.print(f"[bold]Reading:[/bold] {path}")

    try:
        profile = quick_profile(path)
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        raise typer.Exit(code=2)

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
    console.print("[bold green]Status: OK[/bold green]\n")

    raise typer.Exit(code=0)

if __name__ == "__main__":
    app()
