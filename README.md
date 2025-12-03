# Data Validator

Simple, fast data validation for pandas DataFrames and CSV/Parquet files.

## Python API (primary)

```python
import datavalidator as dv
import pandas as pd

df = pd.read_csv("data.csv")
report = dv.validate(df)

if report.has_warnings:
    print("Issues found")
    print(report.to_json())
