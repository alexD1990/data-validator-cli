# src/dfguard/renderer.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .report import ValidationReport
from .rules.base import ValidationResult

console = Console()


def render_console(report: ValidationReport):
    """
    Render complete fact-based validation report.
    Always prints the same 4 sections + final status.
    """
    _render_summary(report)
    _render_structural(report)
    _render_quality(report)
    _render_numeric(report)
    _render_status(report)


# -------------------------
# SUMMARY SECTION
# -------------------------

def _render_summary(report: ValidationReport):
    profile = report.profile

    console.print("\n[bold cyan]Data Summary[/bold cyan]")

    console.print(f"  Rows: {profile.get('rows', 0):,}")
    console.print(f"  Columns: {profile.get('columns', 0)}")

    colnames = profile.get("column_names", [])
    if colnames:
        console.print(f"  Column names: {', '.join(colnames)}")


# -------------------------
# STRUCTURAL SECTION
# -------------------------

def _render_structural(report: ValidationReport):
    console.print("\n[bold cyan]Structural[/bold cyan]")

    results = report.structural_results or []

    if not results:
        console.print("  • No structural checks")
        return

    for r in results:
        _render_result(r)


# -------------------------
# QUALITY SECTION
# -------------------------

def _render_quality(report: ValidationReport):
    console.print("\n[bold cyan]Quality[/bold cyan]")

    results = report.quality_results or []

    if not results:
        console.print("  • No quality checks")
        return

    for r in results:
        _render_result(r)


# -------------------------
# NUMERIC SECTION
# -------------------------

def _render_numeric(report: ValidationReport):
    console.print("\n[bold cyan]Numeric Distribution[/bold cyan]")

    numeric_stats = report.profile.get("numeric_stats", {})

    if not numeric_stats:
        console.print("  • No numeric columns")
        return

    # Print summary statistics per numeric column
    for col, stats in numeric_stats.items():
        min_val = stats.get("min")
        max_val = stats.get("max")
        mean = stats.get("mean")
        median = stats.get("median")
        std = stats.get("std")

        console.print(
            f"  • {col}: "
            f"[{min_val} → {max_val}], "
            f"mean {mean:.2f}, median {median:.2f}, std {std:.2f}"
        )

        # Check for outliers in numeric results
        outlier_info = _find_outlier_info(report.numeric_results, col)
        if outlier_info:
            count = outlier_info.get("count", 0)
            ratio = outlier_info.get("ratio", "0%")
            console.print(f"    [yellow]⚠ {count} outliers ({ratio})[/yellow]")


# -------------------------
# RESULT RENDERING BLOCK
# -------------------------

def _render_result(result: ValidationResult):
    symbol = "⚠" if result.warning else "•"
    color = "yellow" if result.warning else "white"

    console.print(f"  [{color}]{symbol} {result.message}[/{color}]")

    details = result.details or {}
    for key, value in details.items():

        # Nested mapping (per-column)
        if isinstance(value, dict):
            for subkey, subval in value.items():
                console.print(f"     - {subkey}: {subval}")
        else:
            console.print(f"     - {key}: {value}")


# -------------------------
# FINAL STATUS SECTION
# -------------------------

def _render_status(report: ValidationReport):
    console.print()

    status = report.status
    if status == "error":
        console.print("[bold red]✗ Status: ERROR[/bold red]")
    elif status == "warning":
        console.print("[bold yellow]⚠ Status: WARNING[/bold yellow]")
    else:
        console.print("[bold green]✓ Status: OK[/bold green]")

    console.print()


# -------------------------
# HELPERS
# -------------------------

def _find_outlier_info(numeric_results, colname):
    """Find outlier stats inside numeric rule results."""
    for res in (numeric_results or []):
        if not res or not res.details:
            continue
        
        # NumericOutlierRule produces: details={col: {...}}
        if colname in res.details:
            return res.details[colname]

    return None
