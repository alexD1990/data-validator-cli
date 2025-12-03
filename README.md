# dfguard

Guard your DataFrames - Simple data validation for pandas

## Installation
```bash
pip install dfguard
```

## Python API (Primary)
```python
import dfguard
import pandas as pd

df = pd.read_csv("data.csv")
report = dfguard.validate(df)

print(report.status)  # 'ok', 'warning', or 'error'

if report.has_warnings:
    print("Issues found:")
    for result in report.all_results:
        if result and result.warning:
            print(f"  - {result.message}")

# Get JSON
json_output = report.to_json()
```

## CLI (Optional)
```bash
dfguard data.csv
dfguard data.parquet --json
```

## Rules

dfguard checks for:
- Empty datasets
- High null ratios
- Duplicate rows
- Type inconsistencies
- Numeric outliers
- Whitespace issues

## For Databricks Users
```python
# In notebook
import dfguard

# Direct DataFrame validation
report = dfguard.validate(spark_df.toPandas())
display(report.to_dict())
```