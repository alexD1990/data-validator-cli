from pyspark.sql import DataFrame
from dfguard.rules.base import BaseRule, ValidationResult


class SparkNonEmptyRule(BaseRule):
    name = "spark_non_empty"

    def apply(self, profile: dict) -> ValidationResult:
        df: DataFrame = profile["df_spark"]
        rows = df.count()

        # Debug: Print the number of rows to verify if the rule is applied
        print(f"Checking if dataset is empty: {rows} rows")

        if rows == 0:
            return ValidationResult(
                warning=True,
                message="Dataset is empty",
                details={"rows": rows},
            )
        return ValidationResult(
            warning=False,
            message="Dataset is non-empty",
            details={"rows": rows},
        )


class SparkDuplicateRule(BaseRule):
    name = "spark_duplicate_rows"

    def apply(self, profile: dict) -> ValidationResult:
        df: DataFrame = profile["df_spark"]

        # Count the total rows
        rows = df.count()

        # Use dropDuplicates() to find duplicate rows (this removes duplicates)
        df_dedup = df.dropDuplicates()

        # Count the rows after dropping duplicates
        dedup_rows = df_dedup.count()

        # Calculate the number of duplicate rows
        dup_count = rows - dedup_rows
        ratio = dup_count / rows if rows else 0.0

        return ValidationResult(
            warning=(dup_count > 0),
            message="Duplicate rows",
            details={
                "count": dup_count,
                "ratio": f"{ratio:.1%}",
                "total_rows": rows,
            },
        )

