# src/validator/core.py
from typing import Any, Dict

import pandas as pd

from .profiler import profile_dataframe
from .engine import RuleEngine, ValidationReport
from .rules.structural import NonEmptyRule, DuplicateRule
from .rules.quality import NullRatioRule, TypeMismatchRule, WhitespaceRule
from .rules.numeric import NumericOutlierRule


def _build_default_engine() -> RuleEngine:
    """
    Construct the default RuleEngine with all built-in rules.

    This is the single source of truth for which rules are applied,
    used by both the Python API and the CLI.
    """
    return RuleEngine(
        structural_rules=[
            NonEmptyRule(),
            DuplicateRule(),
        ],
        quality_rules=[
            NullRatioRule(),
            TypeMismatchRule(),
            WhitespaceRule(),
        ],
        numeric_rules=[
            NumericOutlierRule(),
        ],
    )


def validate(df: pd.DataFrame) -> ValidationReport:
    """
    Primary public API: validate a pandas DataFrame.

    Example:
        import datavalidator as dv

        report = dv.validate(df)
        if report.has_warnings:
            print("Issues found")
            print(report.to_json())
    """
    profile = profile_dataframe(df)
    engine = _build_default_engine()
    return engine.run(profile)


def validate_profile(profile: Dict[str, Any]) -> ValidationReport:
    """
    Internal helper: validate an already-profiled dataset.

    Used by the CLI to avoid re-running profiling logic when the
    file has already been loaded and profiled.

    Not part of the public API contract, but safe to use internally.
    """
    engine = _build_default_engine()
    return engine.run(profile)
