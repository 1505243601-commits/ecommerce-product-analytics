# 原始数据放置说明

将 Kaggle 下载并解压后的以下文件直接放在 `data/raw/`：

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_products_dataset.csv`

`src/build_mart.py` 不会修改原始 CSV，只会在 `data/analytics/` 写入可供 SQL 和 BI 使用的分析表。
