import json
from dataclasses import dataclass
from typing import List, Optional, Sequence, Dict, Any

import pandas as pd
import numpy as np

from .rules.base import BaseRule, ValidationResult
from .version import __version__

def _to_native(value):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(value, (np.integer, )):
        return int(value)
    if isinstance(value, (np.floating, )):
        return float(value)
    if isinstance(value, (np.ndarray, )):
        return value.tolist()
    return value

@dataclass
class ValidationReport:
    """
    Full validation report for both console and JSON output.
    """
    profile: Dict[str, Any]
    structural_results: List[ValidationResult]
    quality_results: List[ValidationResult]
    numeric_results: List[ValidationResult]

    @property
    def all_results(self) -> List[ValidationResult]:
        return self.structural_results + self.quality_results + self.numeric_results

    @property
    def has_warnings(self) -> bool:
        return any(r.warning for r in self.all_results)

    def _type_breakdown(self) -> Dict[str, int]:
        df = self.profile.get("df")
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

        return {
            "text": text_cols,
            "numeric": numeric_cols,
            "other": other_cols,
        }

    def _numeric_section(self) -> Dict[str, Any]:
        df = self.profile.get("df")
        numeric_stats = self.profile.get("numeric_stats", {}) or {}

        if df is None or not numeric_stats:
            return {"columns": {}}

        # Outlier data fra NumericOutlierRule
        outlier_data: Dict[str, Dict[str, Any]] = {}
        for r in self.numeric_results:
            if not r.details:
                continue
            cols = r.details.get("columns")
            if not isinstance(cols, dict):
                continue
            for col, info in cols.items():
                outlier_data[col] = info

        columns: Dict[str, Any] = {}

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

            col_entry: Dict[str, Any] = {
                "range": [_to_native(col_min), _to_native(col_max)],
                "median": _to_native(median),
                "mean": _to_native(mean),
                "std": _to_native(std),
                "iqr": [_to_native(q1), _to_native(q3)],
            }

            # Outliers
            if col in outlier_data:
                out_info = outlier_data[col]
                col_entry["outliers"] = {
                    "count": int(out_info.get("count", 0)),
                    "ratio": float(out_info.get("ratio", 0.0)),
                }

            # Flags (skew / range)
            flags: List[str] = []
            if mean is not None and median != 0 and mean > 2 * median:
                flags.append("skewed")
            if mean is not None and std is not None and col_max is not None:
                if col_max > mean + 3 * std:
                    flags.append("high_range")

            if flags:
                col_entry["flags"] = [_to_native(f) for f in flags]

            columns[col] = col_entry

        return {"columns": columns}

    def to_json(self) -> str:
        df = self.profile.get("df")
        return json.dumps(
            {
                "validator_version": __version__,
                "file": self.profile.get("path"),
                "summary": {
                    "rows": _to_native(self.profile.get("rows", 0)),
                    "columns": _to_native(self.profile.get("columns", 0)),
                    "types": self._type_breakdown(),
                },
                "structural": [r.to_dict() for r in self.structural_results],
                "quality": [r.to_dict() for r in self.quality_results],
                "numeric": self._numeric_section(),
                "status": "warning" if self.has_warnings else "ok",
            },
            indent=2,
        )


class RuleEngine:
    """
    Executes validation rules grouped by category and returns a structured report.
    Presentation/rendering is handled elsewhere.
    """

    def __init__(
        self,
        structural_rules: Optional[Sequence[BaseRule]] = None,
        quality_rules: Optional[Sequence[BaseRule]] = None,
        numeric_rules: Optional[Sequence[BaseRule]] = None,
    ) -> None:
        self.structural_rules: List[BaseRule] = list(structural_rules or [])
        self.quality_rules: List[BaseRule] = list(quality_rules or [])
        self.numeric_rules: List[BaseRule] = list(numeric_rules or [])

    def _run_bucket(self, rules: List[BaseRule], profile: dict) -> List[ValidationResult]:
        results: List[ValidationResult] = []

        for rule in rules:
            try:
                result = rule.apply(profile)

                # Case 1: Rule suppressed OK-case → ignore
                if result is None:
                    continue

                # Case 2: Valid result (must be ValidationResult)
                if isinstance(result, ValidationResult):
                    results.append(result)
                    continue

                # Case 3: Invalid return type → error
                raise ValueError(
                    f"Rule {getattr(rule, 'name', rule.__class__.__name__)} "
                    f"returned invalid result type: {type(result)}"
                )

            except Exception as e:
                # register rule failure
                results.append(
                    ValidationResult(
                        warning=True,
                        message=f"Rule '{getattr(rule, 'name', rule.__class__.__name__)}' failed",
                        details={"error": str(e)},
                    )
                )

        return results


    def run(self, profile: dict) -> ValidationReport:
        structural_results = self._run_bucket(self.structural_rules, profile)
        quality_results = self._run_bucket(self.quality_rules, profile)
        numeric_results = self._run_bucket(self.numeric_rules, profile)

        return ValidationReport(
            profile=profile,
            structural_results=structural_results,
            quality_results=quality_results,
            numeric_results=numeric_results,
        )
