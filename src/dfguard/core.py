# src/dfguard/core.py

from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .profiler import profile_dataframe
from .engine import RuleEngine
from .report import ValidationReport

# Structural rules
from .rules.structural import NonEmptyRule, DuplicateRule

# Quality rules
from .rules.quality import WhitespaceRule, NullRatioRule, TypeMismatchRule

# Numeric rules
from .rules.numeric import NumericOutlierRule


def _build_default_engine() -> RuleEngine:
    """
    Construct the RuleEngine with all built-in rules.
    This is the single source of truth for rule ordering.
    """
    return RuleEngine(
        structural_rules=[
            NonEmptyRule(),
            DuplicateRule(),
        ],
        quality_rules=[
            WhitespaceRule(),
            NullRatioRule(),
            TypeMismatchRule(),
        ],
        numeric_rules=[
            NumericOutlierRule(),
        ],
    )


def validate(df: pd.DataFrame) -> ValidationReport:
    """
    Public API: Validate a pandas DataFrame and return a ValidationReport.
    ALWAYS returns ValidationReport (never ValidationResult).
    """
    profile = profile_dataframe(df)
    engine = _build_default_engine()
    report = engine.run(profile)

    # Hard contract check:
    if not isinstance(report, ValidationReport):
        raise TypeError(
            f"validate() must return ValidationReport, got {type(report)}"
        )

    return report


def validate_profile(profile: Dict[str, Any]) -> ValidationReport:
    """
    Internal helper: validate an already-profiled dataset.
    Used by CLI to avoid redundant profiling.
    """
    engine = _build_default_engine()
    report = engine.run(profile)

    if not isinstance(report, ValidationReport):
        raise TypeError(
            f"validate_profile() must return ValidationReport, got {type(report)}"
        )

    return report
