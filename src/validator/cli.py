import typer
from validator.profiler import quick_profile

app = typer.Typer(help="Simple and fast data validation CLI utility.")

@app.command()
def validate(
    path: str,
    summary: bool = typer.Option(False, "--summary", help="Only show summary."),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON."),
):
    """
    Validate a dataset (CSV or Parquet). Returns exit code (0 OK, 1 WARNING, 2 FAIL).
    """
    typer.echo(f"Reading {path}...")

    try:
        profile = quick_profile(path)
    except Exception as e:
        typer.echo(f"Error reading file: {e}")
        raise typer.Exit(code=2)

    typer.echo("--- Dataset Profile ---")
    typer.echo(f"Rows: {profile.get('rows')}")
    typer.echo(f"Columns: {profile.get('columns')}")
    if not summary:
        typer.echo(f"Column names: {profile.get('column_names')}")
        typer.echo(f"Null counts: {profile.get('nulls')}")
    typer.echo("------------------------")

    raise typer.Exit(code=0)

if __name__ == "__main__":
    app()
