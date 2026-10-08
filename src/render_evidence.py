"""Render dependency-free SVG evidence charts from generated SQLite marts."""

from __future__ import annotations

import html
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "analytics" / "ecommerce.db"
SCREENSHOT_DIR = PROJECT_ROOT / "docs" / "screenshots"


def rows(connection: sqlite3.Connection, query: str) -> list[dict[str, object]]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(query)]


def scaled(value: float, low: float, high: float, start: float, end: float) -> float:
    return (start + end) / 2 if high == low else start + (value - low) * (end - start) / (high - low)


def label(x: float, y: float, value: object, size: int = 14, color: str = "#111827", weight: str = "normal") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(str(value))}</text>'


def dashboard_svg(connection: sqlite3.Connection) -> str:
    kpi = rows(connection, "SELECT COUNT(DISTINCT order_id) orders, COUNT(DISTINCT customer_unique_id) customers, SUM(payment_value) gmv, AVG(payment_value) aov FROM fact_orders")[0]
    monthly = rows(connection, "SELECT order_month, order_count, gmv FROM monthly_kpi ORDER BY order_month")
    categories = rows(connection, "SELECT product_category_name, allocated_gmv FROM category_kpi ORDER BY allocated_gmv DESC LIMIT 8")
    risk_states = rows(connection, "SELECT customer_state, AVG(delivery_delay_days > 0) * 100 late_rate FROM fact_orders GROUP BY customer_state HAVING COUNT(DISTINCT order_id) >= 100 ORDER BY late_rate DESC LIMIT 8")
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="930" viewBox="0 0 1400 930">', '<rect width="1400" height="930" fill="#f8fafc"/>', label(50, 50, "Olist E-commerce Analysis — Reproducible Dashboard Snapshot", 26, weight="bold"), label(50, 78, "Public anonymized historical data | Delivered orders only | Generated from ecommerce.db", 14, "#475569")]
    labels = ["Delivered orders", "Purchasing customers", "GMV", "Average order value"]
    values = [f"{kpi['orders']:,}", f"{kpi['customers']:,}", f"{kpi['gmv']:,.2f}", f"{kpi['aov']:,.2f}"]
    for index, (name, value) in enumerate(zip(labels, values, strict=True)):
        left = 50 + index * 335
        parts += [f'<rect x="{left}" y="110" width="300" height="95" rx="12" fill="#ffffff" stroke="#e2e8f0"/>', label(left + 18, 145, value, 25, weight="bold"), label(left + 18, 178, name, 14, "#475569")]

    left, top, width, height = 70, 280, 1240, 205
    gmvs = [float(row["gmv"]) for row in monthly]
    orders = [float(row["order_count"]) for row in monthly]
    gmv_points, order_points = [], []
    parts += [label(left, top - 22, "Monthly GMV and order volume", 20, weight="bold"), f'<rect x="{left}" y="{top}" width="{width}" height="{height}" fill="#ffffff" stroke="#e2e8f0"/>']
    for index, row in enumerate(monthly):
        x = scaled(index, 0, len(monthly) - 1, left + 35, left + width - 20)
        gmv_points.append(f"{x:.1f},{scaled(float(row['gmv']), min(gmvs), max(gmvs), top + height - 25, top + 20):.1f}")
        order_points.append(f"{x:.1f},{scaled(float(row['order_count']), min(orders), max(orders), top + height - 25, top + 20):.1f}")
        if index % 4 == 0:
            parts.append(label(x - 18, top + height + 20, row["order_month"], 11, "#64748b"))
    parts += [f'<polyline points="{" ".join(gmv_points)}" fill="none" stroke="#2563eb" stroke-width="3"/>', f'<polyline points="{" ".join(order_points)}" fill="none" stroke="#f97316" stroke-width="3"/>', label(left + 10, top + 20, "GMV", 12, "#2563eb", "bold"), label(left + 55, top + 20, "Orders", 12, "#f97316", "bold")]

    charts = [("Top categories by allocated GMV", categories, "product_category_name", "allocated_gmv", "#0f766e", lambda number: f"{number / 1000:.0f}k"), ("Delivery-risk states (min. 100 orders)", risk_states, "customer_state", "late_rate", "#dc2626", lambda number: f"{number:.1f}%")]
    for chart_index, (title, chart_rows, name_key, value_key, color, formatter) in enumerate(charts):
        chart_left, chart_top, chart_width = 70 + chart_index * 650, 590, 570
        maximum = max(float(row[value_key]) for row in chart_rows)
        parts += [label(chart_left, chart_top - 22, title, 19, weight="bold"), f'<rect x="{chart_left}" y="{chart_top}" width="{chart_width}" height="280" fill="#ffffff" stroke="#e2e8f0"/>']
        for row_index, row in enumerate(reversed(chart_rows)):
            y, value = chart_top + 25 + row_index * 30, float(row[value_key])
            bar_width = scaled(value, 0, maximum, 0, 340)
            parts += [label(chart_left + 12, y + 14, row[name_key], 11, "#334155"), f'<rect x="{chart_left + 210}" y="{y}" width="{bar_width:.1f}" height="18" rx="4" fill="{color}"/>', label(chart_left + 560, y + 14, formatter(value), 11, "#334155")]
    parts.append('</svg>')
    return "\n".join(parts)


def cohort_svg(connection: sqlite3.Connection) -> str:
    retention = rows(connection, "SELECT cohort_month, cohort_index, retention_rate * 100 retention_rate_pct FROM cohort_retention ORDER BY cohort_month, cohort_index")
    cohorts = sorted({str(row["cohort_month"]) for row in retention})
    indices = sorted({int(row["cohort_index"]) for row in retention})
    values = {(str(row["cohort_month"]), int(row["cohort_index"])): float(row["retention_rate_pct"]) for row in retention}
    left, top, cell_width, cell_height = 145, 110, 42, 27
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820">', '<rect width="1200" height="820" fill="#f8fafc"/>', label(45, 48, "Cohort retention by first purchase month", 26, weight="bold"), label(45, 76, "Retention rate = active customers / customers in the first-purchase cohort", 14, "#475569")]
    for column, index in enumerate(indices):
        parts.append(label(left + column * cell_width + 8, top - 12, index, 11, "#475569"))
    for row_index, cohort in enumerate(cohorts):
        y = top + row_index * cell_height
        parts.append(label(55, y + 18, cohort, 12, "#334155"))
        for column, index in enumerate(indices):
            value = values.get((cohort, index))
            opacity = 0 if value is None else 0.15 + 0.85 * value / 100
            fill = "#ffffff" if value is None else f"rgba(37, 99, 235, {opacity:.3f})"
            x = left + column * cell_width
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_width - 2}" height="{cell_height - 2}" fill="{fill}" stroke="#e2e8f0"/>')
            if value is not None and (index == 0 or value >= 5):
                parts.append(label(x + 3, y + 18, f"{value:.1f}", 9, "#0f172a"))
    parts += [label(left, top + len(cohorts) * cell_height + 35, "Columns: months since first purchase", 12, "#475569"), '</svg>']
    return "\n".join(parts)


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Missing {DATABASE_PATH}. Run `python src/build_mart.py` first.")
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        (SCREENSHOT_DIR / "dashboard_overview.svg").write_text(dashboard_svg(connection), encoding="utf-8")
        (SCREENSHOT_DIR / "cohort_retention.svg").write_text(cohort_svg(connection), encoding="utf-8")
    print(f"Rendered evidence charts to {SCREENSHOT_DIR}")


if __name__ == "__main__":
    main()
