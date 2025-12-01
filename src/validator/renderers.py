from typing import Dict, List

import pandas as pd
from rich.console import Console

from validator.engine import ValidationReport
from validator.rules.base import ValidationResult


console = Console()


def _format_ratio(r: float) -> str:
    """Format numeric ratio float → 'xx.xx%'."""
    return f"{r * 100:.2f}%"


def _format_details(details: Dict) -> List[str]:
    """
    Convert details dict into printable structured lines.
    Renderer is responsible for formatting.
    """
    lines = []

    # Case 1: single-level dictionary (quality/structural)
    if "columns" not in details:
        for key, value in details.items():
            if isinstance(value, float):
                value_fmt = _format_ratio(value)
            else:
                value_fmt = str(value)
            lines.append(f"{key}: {value_fmt}")
        return lines

    # Case 2: multi-column structure (numeric outliers)
    for col, info in details["columns"].items():
        count = info["count"]
        ratio = _format_ratio(info["ratio"])
        lines.append(f"{col}: count={count}, ratio={ratio}")

    return lines


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

def render_summary(report: ValidationReport) -> None:
    profile = report.profile
    df = profile.get("df")
    rows = profile.get("rows", 0)
    columns = profile.get("columns", 0)

    text_cols = 0
    numeric_cols = 0
    other_cols = 0

    if df is not None:
        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_numeric_dtype(dtype):
                numeric_cols += 1
            elif pd.api.types.is_string_dtype(dtype) or dtype == object:
                text_cols += 1
            else:
                other_cols += 1

    console.print("\n[bold cyan]Data Summary[/bold cyan]")
    console.print(f" Rows:    │ {rows}")
    console.print(f" Columns: │ {columns}")
    console.print(f" Types:   │ {text_cols} text, {numeric_cols} numeric, {other_cols} other")


# ------------------------------------------------------------
# Structural Checks
# ------------------------------------------------------------

def render_structural(results: List[ValidationResult]) -> None:
    console.print("\n[bold]Structural Checks[/bold]")

    warnings = [r for r in results if r.warning]

    if warnings:
        for r in warnings:
            console.print(f" ⚠ {r.message}")
            if r.details:
                for line in _format_details(r.details):
                    console.print(f"    - {line}")
    else:
        console.print(" ✓ No structural issues detected")


# ------------------------------------------------------------
# Quality Checks
# ------------------------------------------------------------

def render_quality(results: List[ValidationResult]) -> None:
    console.print("\n[bold]Quality Checks[/bold]")

    warnings = [r for r in results if r.warning]

    if warnings:
        for r in warnings:
            console.print(f" ⚠ {r.message}")
            if r.details:
                for line in _format_details(r.details):
                    console.print(f"    - {line}")
    else:
        console.print(" ✓ No quality issues detected")


# ------------------------------------------------------------
# Numeric Distribution (descriptive section)
# ------------------------------------------------------------

def render_numeric(report: ValidationReport) -> None:
    profile = report.profile
    df = profile.get("df")
    numeric_stats = profile.get("numeric_stats", {}) or {}

    console.print("\n[bold]Numeric Distribution[/bold]")

    if df is None or not numeric_stats:
        console.print(" (no numeric columns)")
        return

    # Collect outlier counts from numeric_results
    outlier_data = {}
    for r in report.numeric_results:
        if not r.details:
            continue
        cols = r.details.get("columns")
        if not isinstance(cols, dict):
            continue
        for col, info in cols.items():
            outlier_data[col] = info

    for col, stats in numeric_stats.items():
        s = df[col].dropna()
        if s.empty:
            continue

        col_min = stats["min"]
        col_max = stats["max"]
        mean = stats["mean"]
        std = stats["std"]

        median = float(s.median())
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1

        # Build warning parts
        parts = []

        # Only warn if >0 outliers
        if col in outlier_data:
            count = outlier_data[col]["count"]
            if count > 0:
                ratio = outlier_data[col]["ratio"]
                parts.append(f"{count} outliers ({_format_ratio(ratio)})")

        # Suspicious distribution
        skew = (mean > 2 * median) if (mean is not None and median != 0) else False
        if skew:
            parts.append("suspicious distribution")

        warn_suffix = ""
        if parts:
            warn_suffix = " ⚠ " + " – ".join(parts)

        console.print(f" • {col}: [{col_min} → {col_max}], median {median}{warn_suffix}")

        # Conditional detail
        if skew and mean is not None:
            console.print(f"    - mean {mean:.2f} >> median {median:.2f}")
        console.print(f"    - IQR [{q1:.2f} → {q3:.2f}]")


# ------------------------------------------------------------
# Validation Status
# ------------------------------------------------------------

def render_status(report: ValidationReport) -> None:
    any_warning = report.has_warnings

    console.print()
    if any_warning:
        console.print("[yellow]Status: WARNING[/yellow]")
    else:
        console.print("[bold green]Status: OK[/bold green]")
