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
