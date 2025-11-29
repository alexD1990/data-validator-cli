# Data Validator CLI

Lightweight and fast command-line tool for basic dataset sanity checks before further analysis.

The goal is simple:

* Validate a dataset (CSV or Parquet) quickly and clearly without having to open a notebook.

Ideal for:
- Quick pre-check before data ingestion or transformation
- CI/CD validation steps
- Identifying obvious schema issues, null problems, or structural anomalies

---

## Current status
 **Prototype phase (v0.1)**  
Basic CLI structure + lightweight dataset profiling.

---

## Usage (early prototype)

```bash
validate data.csv
```