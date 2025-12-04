# src/dfguard/rules/spark/performance.py

from pyspark.sql import DataFrame
from dfguard.rules.base import BaseRule, ValidationResult
import os

class SmallFileRule(BaseRule):
    name = "spark_small_file_problem"

    def apply(self, profile: dict) -> ValidationResult:
        df: DataFrame = profile["df_spark"]
        input_files = df.inputFiles()
        num_files = len(input_files)

        if num_files == 0:
            return ValidationResult(
                warning=False,
                message="No files detected",
                details={"num_files": num_files},
            )

        total_bytes = sum([os.path.getsize(f) for f in input_files])
        avg_mb = (total_bytes / num_files) / (1024 * 1024)

        if num_files > 100 and avg_mb < 10:
            return ValidationResult(
                warning=True,
                message="Small file problem detected",
                details={
                    "num_files": num_files,
                    "avg_size_mb": round(avg_mb, 2),
                    "total_size_mb": round(total_bytes / (1024 * 1024), 2),
                    "recommendation": "Consider optimizing the dataset.",
                },
            )

        return ValidationResult(
            warning=False,
            message="No small file problem detected",
            details={"num_files": num_files, "avg_size_mb": round(avg_mb, 2)},
        )
