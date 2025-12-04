from pyspark.sql import DataFrame
from pyspark.sql.functions import sum as spark_sum
from dfguard.rules.base import BaseRule, ValidationResult


class SparkNullRatioRule(BaseRule):
    name = "spark_null_ratio"

    def apply(self, profile: dict) -> ValidationResult:
        df: DataFrame = profile["df_spark"]
        
        numeric_columns = [col for col, dtype in df.dtypes if dtype in ["int", "double", "float"]]
        
        if not numeric_columns:
            return ValidationResult(
                warning=False,
                message="No numeric columns to check for nulls",
                details={"null_ratio": "N/A", "total_nulls": 0, "total_cells": 0},
            )

        null_counts = df.select([df[c].isNull().cast("int").alias(c) for c in numeric_columns])
        null_counts_aggregated = null_counts.agg(*[spark_sum(c).alias(c) for c in numeric_columns]).collect()[0].asDict()

        total_nulls = sum(null_counts_aggregated.values())
        total_cells = df.count() * len(numeric_columns)
        null_ratio = total_nulls / total_cells if total_cells else 0

        return ValidationResult(
            warning=(null_ratio > 0.1),
            message="Null ratio",
            details={"null_ratio": f"{null_ratio:.1%}", "total_nulls": total_nulls, "total_cells": total_cells},
        )

class SparkTypeMismatchRule(BaseRule):
    name = "spark_type_mismatch"

    def apply(self, profile: dict) -> ValidationResult:
        df: DataFrame = profile["df_spark"]
        mismatched_columns = []
        for column, dtype in df.dtypes:
            if dtype not in ["string", "int", "double", "float", "long", "short", "boolean", "timestamp", "date"]:  # Example mismatch check
                mismatched_columns.append(column)

        if mismatched_columns:
            return ValidationResult(
                warning=True,
                message="Type mismatch in columns",
                details={"columns": mismatched_columns},
            )

        return ValidationResult(
            warning=False,
            message="Type consistency",
            details={"columns": "All columns are consistent."},
        )