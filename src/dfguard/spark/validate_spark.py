# src/dfguard/spark/validate_spark.py

from __future__ import annotations

from typing import Any, Dict, Optional

from pyspark.sql import DataFrame as SparkDataFrame

from dfguard.spark.engine import SparkRuleEngine


def _profile_spark_dataframe(df: SparkDataFrame, table_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Minimal Spark profiling, analogous to pandas profile_dataframe().
    This profile must satisfy the renderer + JSON builder expectations.
    """
    cols = df.columns
    rows = df.count()  # expensive, but expected at validation time

    profile = {
        "df": None,               # indicates non-pandas backend
        "df_spark": df,           # Spark-native handle
        "rows": rows,
        "columns": len(cols),
        "column_names": cols,
        "types": {c: str(t) for c, t in df.dtypes},
        "numeric_stats": {},      # will be populated properly in Step 3 (numeric rules)
    }

    if table_name:
        profile["path"] = table_name

    return profile


from dfguard.spark.engine import SparkRuleEngine

def validate_spark(df: SparkDataFrame, table_name: Optional[str] = None):
    """
    Public Spark API.
    Returns a ValidationReport (same object used by pandas engine).
    """
    profile = _profile_spark_dataframe(df, table_name)

    print(profile)

    # Initialize the engine with the rules (not empty lists)
    engine = SparkRuleEngine()  # This will use the rules defined in the SparkRuleEngine class

    return engine.run(profile)

