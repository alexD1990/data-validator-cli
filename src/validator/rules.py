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
