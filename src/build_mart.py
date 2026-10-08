"""Build analysis-ready Olist e-commerce marts from public raw CSV files."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"

REQUIRED_FILES = {
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
}


def read_source(name: str) -> pd.DataFrame:
    path = RAW_DIR / REQUIRED_FILES[name]
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path.name}. Download the Olist CSV files into {RAW_DIR}."
        )
    return pd.read_csv(path)


def prepare_fact_orders() -> pd.DataFrame:
    orders = read_source("orders")
    items = read_source("items")
    payments = read_source("payments")
    customers = read_source("customers")

    orders = orders.loc[orders["order_status"].eq("delivered")].copy()
    for column in [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]:
        orders[column] = pd.to_datetime(orders[column], errors="coerce")

    item_summary = (
        items.groupby("order_id", as_index=False)
        .agg(
            item_count=("order_item_id", "count"),
            product_count=("product_id", "nunique"),
            seller_count=("seller_id", "nunique"),
            item_revenue=("price", "sum"),
            freight_value=("freight_value", "sum"),
        )
    )
    payment_summary = (
        payments.groupby("order_id", as_index=False)
        .agg(
            payment_value=("payment_value", "sum"),
            payment_installments=("payment_installments", "max"),
        )
    )
    primary_payment = (
        payments.sort_values(["order_id", "payment_sequential"])
        .drop_duplicates("order_id")[["order_id", "payment_type"]]
    )

    fact_orders = (
        orders.merge(customers, on="customer_id", how="left")
        .merge(item_summary, on="order_id", how="left")
        .merge(payment_summary, on="order_id", how="left")
        .merge(primary_payment, on="order_id", how="left")
    )
    fact_orders["order_month"] = fact_orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
    fact_orders["delivery_days"] = (
        fact_orders["order_delivered_customer_date"] - fact_orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 86_400
    fact_orders["delivery_delay_days"] = (
        fact_orders["order_delivered_customer_date"] - fact_orders["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86_400
    return fact_orders


def build_monthly_kpi(fact_orders: pd.DataFrame) -> pd.DataFrame:
    return (
        fact_orders.groupby("order_month", as_index=False)
        .agg(
            order_count=("order_id", "nunique"),
            active_customers=("customer_unique_id", "nunique"),
            gmv=("payment_value", "sum"),
            avg_order_value=("payment_value", "mean"),
            avg_delivery_days=("delivery_days", "mean"),
            late_delivery_rate=("delivery_delay_days", lambda values: (values > 0).mean()),
        )
        .sort_values("order_month")
    )


def build_cohort_retention(fact_orders: pd.DataFrame) -> pd.DataFrame:
    customer_month = fact_orders[["customer_unique_id", "order_month"]].drop_duplicates()
    first_order = (
        customer_month.groupby("customer_unique_id", as_index=False)["order_month"]
        .min()
        .rename(columns={"order_month": "cohort_month"})
    )
    cohort = customer_month.merge(first_order, on="customer_unique_id", how="inner")
    cohort["cohort_index"] = (
        pd.PeriodIndex(cohort["order_month"], freq="M").astype(int)
        - pd.PeriodIndex(cohort["cohort_month"], freq="M").astype(int)
    )
    retained = (
        cohort.groupby(["cohort_month", "cohort_index"], as_index=False)
        .agg(active_customers=("customer_unique_id", "nunique"))
    )
    cohort_size = retained.loc[retained["cohort_index"].eq(0), ["cohort_month", "active_customers"]]
    cohort_size = cohort_size.rename(columns={"active_customers": "cohort_size"})
    retained = retained.merge(cohort_size, on="cohort_month", how="left")
    retained["retention_rate"] = retained["active_customers"] / retained["cohort_size"]
    return retained.sort_values(["cohort_month", "cohort_index"])


def build_category_kpi(fact_orders: pd.DataFrame) -> pd.DataFrame:
    items = read_source("items")
    products = read_source("products")
    category_orders = (
        items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
        .merge(fact_orders[["order_id", "payment_value"]], on="order_id", how="inner")
    )
    item_counts = category_orders.groupby("order_id")["order_item_id"].transform("count")
    category_orders["allocated_gmv"] = category_orders["payment_value"] / item_counts
    return (
        category_orders.groupby("product_category_name", dropna=False, as_index=False)
        .agg(
            order_count=("order_id", "nunique"),
            item_count=("order_item_id", "count"),
            allocated_gmv=("allocated_gmv", "sum"),
            avg_item_price=("price", "mean"),
        )
        .sort_values("allocated_gmv", ascending=False)
    )


def export_marts() -> None:
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    fact_orders = prepare_fact_orders()
    marts = {
        "fact_orders": fact_orders,
        "monthly_kpi": build_monthly_kpi(fact_orders),
        "cohort_retention": build_cohort_retention(fact_orders),
        "category_kpi": build_category_kpi(fact_orders),
    }

    database_path = ANALYTICS_DIR / "ecommerce.db"
    with sqlite3.connect(database_path) as connection:
        for table_name, dataframe in marts.items():
            dataframe.to_csv(ANALYTICS_DIR / f"{table_name}.csv", index=False)
            dataframe.to_sql(table_name, connection, if_exists="replace", index=False)
            print(f"Built {table_name}: {len(dataframe):,} rows")


if __name__ == "__main__":
    export_marts()
