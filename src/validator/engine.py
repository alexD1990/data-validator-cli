from typing import List
from rich.console import Console
from validator.rules.base import BaseRule, ValidationResult

console = Console()

class RuleEngine:
    def __init__(self, rules: List[BaseRule]):
        self.rules = rules

    def run(self, profile: dict) -> List[ValidationResult]:
        results = []
        for rule in self.rules:
            try:
                result = rule.apply(profile)
                if not isinstance(result, ValidationResult):
                    raise ValueError(f"Rule {rule.name} returned invalid result type.")
                results.append(result)
            except Exception as e:
                # Crash-safe rule handling
                results.append(
                    ValidationResult(
                        warning=True,
                        message=f"Rule '{rule.name}' failed: {e}",
                        details={}
                    )
                )
        return results

    def render_console(self, results: List[ValidationResult]):
        warnings = [r for r in results if r.warning]

        if warnings:
            console.print("[yellow] Status: WARNING[/yellow]")
            for w in warnings:
                console.print(f" • {w.message}")
                if w.details:
                    for k, v in w.details.items():
                        console.print(f"    - {k}: {v}")
        else:
            console.print("[bold green] Status: OK[/bold green]")
