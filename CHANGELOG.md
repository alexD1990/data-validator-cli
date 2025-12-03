# Changelog

## [1.0.0] - 2025-12-03

### Added
- Python API (`dfguard.validate(df)`)
- CLI tool (`dfguard data.csv`)
- CSV and Parquet support
- JSON output mode
- 6 validation rules:
  - Empty dataset detection
  - Null ratio warnings
  - Duplicate row detection
  - Type consistency checks
  - Numeric outlier detection
  - Whitespace issue detection

### Architecture
- Complete ValidationReport with status computation
- Type-safe API contract
- Test suite with 47 tests
- CLI/API parity verified