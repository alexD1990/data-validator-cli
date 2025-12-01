import os
import pandas as pd


def quick_profile(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".parquet":
        df = pd.read_parquet(path)
    elif ext == ".csv":
        df = pd.read_csv(path, nrows=50000)
    else:
        raise ValueError(f"Unsupported format: {path}")

    numeric_cols = df.select_dtypes(include=["number"]).columns
    numeric_stats = {}
    for col in numeric_cols:
        if len(df[col].dropna()) == 0:
            continue
        numeric_stats[col] = {
            "min": df[col].min(),
            "max": df[col].max(),
            "mean": df[col].mean(),
            "std": df[col].std(),
        }

    return {
        "path": path,
        "df": df,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "nulls": df.isna().sum().to_dict(),
        "numeric_stats": numeric_stats,
    }
