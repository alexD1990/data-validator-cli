# src/validator/profiler.py
import os
from typing import Any, Dict

import pandas as pd


def profile_dataframe(df: pd.DataFrame, *, source: str | None = None) -> Dict[str, Any]:
    """
    Core profiling logic.

    Accepts a pandas DataFrame directly and returns the profile dict
    used by the RuleEngine and renderers.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns
    numeric_stats: Dict[str, Dict[str, float]] = {}

    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        numeric_stats[col] = {
            "min": series.min(),
            "max": series.max(),
            "mean": series.mean(),
            "std": series.std(),
        }

    profile: Dict[str, Any] = {
        "df": df,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "nulls": df.isna().sum().to_dict(),
        "numeric_stats": numeric_stats,
    }

    # Preserve path information when available (for JSON output)
    if source is not None:
        profile["path"] = source

    return profile


def quick_profile(path: str) -> Dict[str, Any]:
    """
    Backwards-compatible wrapper used by the CLI.

    - Loads the file from disk
    - Builds a profile using profile_dataframe(df)
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".parquet":
        df = pd.read_parquet(path)
    elif ext == ".csv":
        df = pd.read_csv(path, nrows=50000)
    else:
        raise ValueError(f"Unsupported format: {path}")

    return profile_dataframe(df, source=path)
