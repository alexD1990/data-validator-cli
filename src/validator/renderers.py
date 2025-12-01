from typing import List, Dict

import pandas as pd
from rich.console import Console
from rich.table import Table

from validator.engine import ValidationReport
from validator.rules.base import ValidationResult

console = Console()


def render_summary(profile: Dict) -> None:
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
    table = Table(show_header=False, show_edge=False)
    table.add_row("Rows:", str(rows))
    table.add_row("Columns:", str(columns))
    table.add_row("Types:", f"{text_cols} text, {numeric_cols} numeric, {other_cols} other")
    console.print(table)


def render_structural(structural_results: List[ValidationResult]) -> None:
    console.print("\n[bold]Structural Checks[/bold]")

    if not structural_results:
        console.print(" • (no structural rules configured)")
        return

    for res in structural_results:
        status = "⚠" if res.warning else "✓"
        msg = res.message
        console.print(f" • {msg} {status}")
        if res.details:
            for k, v in res.details.items():
                console.print(f"    - {k}: {v}")


def render_quality(quality_results: List[ValidationResult]) -> None:
    console.print("\n[bold]Quality Checks[/bold]")

    # Vi viser kun faktiske warnings her, for å holde det kompakt
    warnings = [r for r in quality_results if r.warning]

    if not warnings:
        console.print(" • No quality issues detected")
        return

    for res in warnings:
        console.print(f" • {res.message}")
        if res.details:
            for k, v in res.details.items():
                console.print(f"    - {k}: {v}")


def render_numeric(profile: Dict, numeric_results: List[ValidationResult]) -> None:
    df = profile.get("df")
    numeric_stats = profile.get("numeric_stats", {})

    console.print("\n[bold]Numeric Distribution[/bold]")

    if df is None or not numeric_stats:
        console.print(" • (no numeric columns)")
        return

    # Map outlier-info per kolonne fra numeric rules
    outlier_counts: Dict[str, int] = {}
    for res in numeric_results:
        if res.warning and res.details:
            for col, count in res.details.items():
                outlier_counts[col] = int(count)

    for col, stats in numeric_stats.items():
        series = df[col].dropna()
        if series.empty:
            continue

        col_min = stats.get("min")
        col_max = stats.get("max")
        mean = stats.get("mean")
        std = stats.get("std")

        median = float(series.median())
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1

        # Heuristikker for "mistenkelig" distribusjon
        skew_flag = False
        extreme_range_flag = False

        if mean is not None and median is not None and median != 0:
            if mean > 2 * median:
                skew_flag = True

        if mean is not None and std is not None and col_max is not None:
            if col_max > mean + 3 * std:
                extreme_range_flag = True

        outliers = outlier_counts.get(col)
        warn_parts = []
        if outliers:
            total = len(series)
            ratio = outliers / total if total else 0
            warn_parts.append(f"{outliers} outliers ({ratio:.2%})")
        if skew_flag or extreme_range_flag:
            warn_parts.append("suspicious distribution")

        warn_suffix = ""
        if warn_parts:
            warn_suffix = " ⚠ " + " – ".join(warn_parts)

        console.print(f" • {col}: [{col_min} → {col_max}], median {median}{warn_suffix}")

        # Conditional detail
        if skew_flag and mean is not None:
            console.print(f"    - mean {mean:.2f} >> median {median:.2f}")
        console.print(f"    - IQR [{q1:.2f} → {q3:.2f}]")


def render_status(report: ValidationReport) -> None:
    any_warning = any(
        r.warning
        for bucket in (report.structural, report.quality, report.numeric)
        for r in bucket
    )
    console.print()
    if any_warning:
        console.print("[yellow]Status: WARNING[/yellow]")
    else:
        console.print("[bold green]Status: OK[/bold green]")
