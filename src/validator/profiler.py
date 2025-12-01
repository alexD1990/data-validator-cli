import pandas as pd

def quick_profile(path: str) -> dict:
    df = pd.read_csv(path, nrows=50000)

    numeric_cols = df.select_dtypes(include=['number']).columns
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
        "df": df,  # Cached DataFrame
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "nulls": df.isna().sum().to_dict(),
        "numeric_stats": numeric_stats,
    }
