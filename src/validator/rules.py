"""
Validation rules for dataset quality checks.

Each rule should:
- Accept the dataset profile (dict)
- Raise SystemExit with appropriate exit code on failure
- Write clear message to console

Exit codes:
    0 = OK
    1 = WARNING (future use)
    2 = FAIL (stop execution)
"""

from typing import Dict
from rich.console import Console

console = Console()


def validate_non_empty(profile: Dict) -> None:
    """
    Rule: Dataset must contain data rows.

    Raises
    -------
    SystemExit(2)
        If the dataset contains zero rows.
    """
    if profile.get("rows", 0) == 0:
        console.print("[bold red] Validation error: dataset contains no data rows[/bold red]")
        raise SystemExit(2)

def warn_high_null_ratio(profile: Dict, threshold: float = 0.5) -> bool:
    """
    Warning rule: If any column has null ratio above threshold, warn user.

    Returns
    -------
    bool
        True if warning was triggered, False otherwise.
    """
    nulls = profile.get("nulls", {})
    row_count = profile.get("rows", 0)

    if row_count == 0:
        return False  # Already handled elsewhere

    warnings = {}
    for col, null_count in nulls.items():
        ratio = null_count / row_count if row_count > 0 else 0
        if ratio > threshold:
            warnings[col] = f"{ratio:.1%}"

    if warnings:
        console.print("\n[bold yellow]Warning: High null ratio detected[/bold yellow]")
        for col, ratio_str in warnings.items():
            console.print(f"  • {col}: {ratio_str} null values")

        return True

    return False

def warn_duplicate_rows(profile: Dict, threshold_ratio: float = 0.01) -> bool:
    """
    Warning rule: detect duplicated full rows.
    
    Parameters
    ----------
    profile : dict
        Profiling result (must include 'df_sample' if enabled later, but for now we'll re-read file).
    threshold_ratio : float
        Ratio threshold for duplicates. e.g. 0.01 for 1%.
    
    Returns
    -------
    bool
        True if warning is triggered, False otherwise.
    """
    rows = profile.get("rows", 0)
    if rows <= 1:
        return False  # Nothing to compare

    # Re-read file (only sample logic was used earlier)
    try:
        import pandas as pd
        df = pd.read_csv(profile["path"], nrows=50000)
    except Exception:
        return False  # Skip if reading fails, avoid blocking validation

    duplicate_count = df.duplicated().sum()
    if duplicate_count == 0:
        return False

    ratio = duplicate_count / rows
    if ratio >= threshold_ratio:
        console.print("\n[bold yellow]Warning: Duplicate rows detected[/bold yellow]")
        console.print(f"  • Count: {duplicate_count} ({ratio:.1%} of dataset)")
        return True
    
    return False

def warn_type_mismatch(profile: Dict, numeric_ratio_threshold: float = 0.8) -> bool:
    """
    Warning rule: detects likely type mismatches in data.
    Example: column appears numeric but contains non-numeric values.
    
    Parameters
    ----------
    profile : dict
        Profile data with basic stats (incl. 'path').
    numeric_ratio_threshold : float
        % of values required to be numeric for us to expect column as numeric.

    Returns
    -------
    bool
        True if warning triggered, else False.
    """
    import pandas as pd

    try:
        df = pd.read_csv(profile["path"], nrows=50000)
    except Exception:
        return False

    warnings = []

    for col in df.columns:
        series = df[col].dropna()

        if len(series) == 0:
            continue  # empty or all null

        # Try convert to numeric and check success ratio
        numeric_mask = pd.to_numeric(series, errors="coerce").notna()
        numeric_ratio = numeric_mask.sum() / len(series)

        if 0 < numeric_ratio < numeric_ratio_threshold:
            warnings.append(f"{col}: {numeric_ratio:.1%} numeric-like")

    if warnings:
        console.print("\n[bold yellow] Warning: Potential type mismatch detected[/bold yellow]")
        for w in warnings:
            console.print(f"  • {w}")
        return True

    return False
