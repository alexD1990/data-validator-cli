from rich.console import Console

console = Console()

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def frame(title: str, lines: list[str]):
    """
    Draw a framed section like:
    ┌─ Title ─────────────────────────────
    │ line
    │ line
    └─────────────────────────────────────
    """
    width = 60

    header = f"┌─ {title} "
    header += "─" * max(0, width - len(header))
    console.print(header)

    for line in lines:
        console.print(f"│ {line}")

    footer = "└" + "─" * (width - 1)
    console.print(footer)
    console.print()  # extra spacing


def _split_zero_nonzero(details, zero_values=("0.0%", "0%")):
    """
    Split columns with issues vs columns clean.
    """
    nonzero = {}
    zero_count = 0
    for col, val in details.items():
        # Handle string percentages
        if isinstance(val, str) and val in zero_values:
            zero_count += 1
            continue

        # Handle ints/floats
        if isinstance(val, (int, float)) and val == 0:
            zero_count += 1
            continue

        # Otherwise nonzero
        nonzero[col] = val

    return nonzero, zero_count


def _fmt_median(median):
    """
    Smart median formatting:
    - Remove trailing .0
    - Round to 2 decimals
    """
    if median is None:
        return "0"
    try:
        m = float(median)
    except:
        return str(median)

    m = round(m, 2)
    if m.is_integer():
        return str(int(m))
    return str(m)


def _fmt_ratio(r):
    """Ensure consistent ratio formatting."""
    if isinstance(r, str):
        return r
    return f"{r:.1%}"


# ------------------------------------------------------------
# Main renderer
# ------------------------------------------------------------

def render_console(report):
    _render_summary(report)
    _render_structural(report)
    _render_quality(report)
    _render_numeric(report)
    _render_status(report)


# ------------------------------------------------------------
# Data Summary
# ------------------------------------------------------------

def _render_summary(report):
    p = report.profile
    df = p.get("df")
    rows = p.get("rows", 0)
    cols = p.get("columns", 0)
    colnames = p.get("column_names") or []

    lines = [f"Rows: {rows:,}"]

    if df is not None:
        num_numeric = len(df.select_dtypes(include=["number"]).columns)
    else:
        num_numeric = 0

    num_text = cols - num_numeric

    lines.append(f"Columns: {cols} ({num_numeric} numeric, {num_text} text)")

    # Column names only if <=6, else truncated
    if len(colnames) <= 6:
        names = ", ".join(colnames)
    else:
        head = ", ".join(colnames[:5])
        remaining = len(colnames) - 5
        names = f"{head}, ... (+{remaining} more)"

    lines.append(f"Names: {names}")

    frame("Data Summary", lines)


# ------------------------------------------------------------
# Structural section
# ------------------------------------------------------------

def _render_structural(report):
    lines = []

    for res in report.structural_results:
        msg = res.message.lower()
        details = res.details or {}

        # IMPORTANT: Check "non-empty" FIRST.
        # Otherwise "dataset non-empty" incorrectly matches "empty".
        if msg == "dataset non-empty":
            lines.append("✓ Dataset contains data")
            continue

        if msg == "dataset empty":
            lines.append("⚠ Dataset is empty")
            continue

        # Duplicate rows (clean phrasing)
        if "duplicate" in msg:
            count = details.get("count", 0)
            ratio = _fmt_ratio(details.get("ratio", "0.0%"))

            if count == 1:
                row_text = "1 duplicate row"
            else:
                row_text = f"{count} duplicate rows"

            symbol = "⚠" if count > 0 else "•"
            lines.append(f"{symbol} Duplicate rows: {row_text} ({ratio})")
            continue

        # Fallback (rare)
        symbol = "⚠" if res.warning else "•"
        lines.append(f"{symbol} {res.message}")
        for k, v in details.items():
            lines.append(f"   - {k}: {v}")

    frame("Structural", lines or ["• No structural checks"])


# ------------------------------------------------------------
# Quality section
# ------------------------------------------------------------

def _render_quality(report):
    lines = []
    rows = report.profile.get("rows", 1) or 1

    for res in report.quality_results:
        msg = res.message.lower()
        details = res.details or {}

        # Null ratio
        if "null ratio" in msg:
            nonzero, zeros = _split_zero_nonzero(details)
            lines.append("• Null ratio:")

            if nonzero:
                for col, val in sorted(nonzero.items()):
                    lines.append(f"   - {col}: {val}")
            if zeros and not nonzero:
                lines.append(f"   - All columns with 0.0%")
            elif zeros:
                lines.append(f"   - {zeros} columns with 0.0%")
            continue

        # Type mismatch
        if "type mismatch" in msg:
            nonzero, zeros = _split_zero_nonzero(details)

            if not nonzero:
                lines.append("• Type consistency:")
                lines.append("   - All columns consistent")
            else:
                for col, val in sorted(nonzero.items()):
                    lines.append(f"⚠ Type mismatch in: {col} ({val})")
            continue

        # Whitespace issues
        if "whitespace" in msg:
            positive = {c: v for c, v in details.items() if v > 0}
            zero_cols = len(details) - len(positive)

            lines.append("• Whitespace issues:")
            if positive:
                for col, cnt in sorted(positive.items()):
                    ratio = cnt / rows
                    lines.append(f"   - {col}: {cnt} rows ({ratio:.1%})")
            if zero_cols and not positive:
                lines.append("   - No whitespace issues")
            elif zero_cols:
                lines.append(f"   - {zero_cols} columns with no whitespace issues")
            continue

        # Fallback
        symbol = "⚠" if res.warning else "•"
        lines.append(f"{symbol} {res.message}")
        for k, v in details.items():
            lines.append(f"   - {k}: {v}")

    frame("Quality", lines or ["• No quality checks"])


# ------------------------------------------------------------
# Numeric Distribution
# ------------------------------------------------------------

def _render_numeric(report):
    p = report.profile
    numeric_stats = p.get("numeric_stats", {})

    if not numeric_stats:
        frame("Numeric Distribution", ["• No numeric columns"])
        return

    lines = []
    first = True

    for col, stats in numeric_stats.items():
        if not first:
            lines.append("")  # Spacer between columns
        first = False

        min_val = stats.get("min")
        max_val = stats.get("max")
        mean = float(stats.get("mean", 0.0) or 0.0)
        median = float(stats.get("median", mean) or mean)
        outlier = _find_outlier_info(report.numeric_results, col)

        # Main line with nice median
        lines.append(f"• {col}: [{min_val} → {max_val}], median {_fmt_median(median)}")

        # Outliers
        if outlier:
            count = outlier.get("count", 0)
            ratio = _fmt_ratio(outlier.get("ratio", "0.0%"))
            symbol = "⚠" if count > 0 else "•"
            lines.append(f"   {symbol} {count} outliers ({ratio})")

        # Skew (only if meaningful)
        if median != 0:
            rel_diff = abs(mean - median) / abs(median)
        else:
            rel_diff = 1 if mean != 0 else 0

        if rel_diff >= 0.5:
            direction = ">>" if mean > median else "<<"
            lines.append(f"   mean={_fmt_median(mean)} ({direction} median, indicates skew)")

    frame("Numeric Distribution", lines)


# ------------------------------------------------------------
# Status
# ------------------------------------------------------------

def _render_status(report):
    if report.status == "error":
        console.print("✗ Status: ERROR", style="bold red")
    elif report.status == "warning":
        console.print("⚠ Status: WARNING", style="bold yellow")
    else:
        console.print("✓ Status: OK", style="bold green")
    console.print()


# ------------------------------------------------------------
# Outlier lookup
# ------------------------------------------------------------

def _find_outlier_info(numeric_results, col):
    for res in numeric_results or []:
        if col in (res.details or {}):
            return res.details[col]
    return None
