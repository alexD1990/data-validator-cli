import pandas as pd

def quick_profile(path: str) -> dict:
    """
    Lightweight profiling of dataset.
    Reads a max of 50k rows for speed.
    """
    df = pd.read_csv(path, nrows=50000)  # Sampling, not full load
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "nulls": df.isna().sum().to_dict(),
    }
