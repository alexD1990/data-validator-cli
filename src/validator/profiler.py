import pandas as pd

def quick_profile(path: str) -> dict:
    """
    Generate a lightweight profile of the dataset.

    Notes
    -----
    - Only reads up to 50k rows for speed
    - Intended for pre-analysis validation
    - Does not perform any cleaning or transforms
    """
    df = pd.read_csv(path, nrows=50000)  # Sampling, not full load
    return {
        "path":path,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "nulls": df.isna().sum().to_dict(),
    }
