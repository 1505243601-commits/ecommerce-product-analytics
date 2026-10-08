# 指标口径与复现证据

## 数据范围

- **数据集**：Kaggle 的 Olist Brazilian E-Commerce Public Dataset；公开、匿名化的历史交易样本，不代表任何真实公司的当前经营结果。
- **分析对象**：仅保留 `order_status = 'delivered'` 的订单；订单粒度为 `order_id`，购买用户粒度为 `customer_unique_id`。
- **时间口径**：按 `order_purchase_timestamp` 归属月份；本次已构建数据覆盖 2016-09 至 2018-08。
- **金额口径**：GMV 为订单支付明细 `payment_value` 按 `order_id` 汇总后的求和，包含运费；缺失支付金额不补零、不外推。
- **延迟口径**：`delivery_delay_days = order_delivered_customer_date - order_estimated_delivery_date`；大于 0 天视为延迟。

## 最终指标

| 指标 | 定义与计算公式 | 粒度/去重规则 |
| --- | --- | --- |
| 已送达订单量 | `COUNT(DISTINCT order_id)` | 已送达订单；订单去重 |
| 购买用户数 | `COUNT(DISTINCT customer_unique_id)` | 已送达订单关联的唯一购买用户 |
| GMV | `SUM(payment_value)` | 订单支付汇总后求和，避免多支付方式导致重复计算 |
| 客单价 | `AVG(payment_value)` | 已送达订单的订单级支付金额均值，即 GMV / 已送达订单量 |
| 活跃购买用户 | 月内 `COUNT(DISTINCT customer_unique_id)` | 以支付下单月份归属 |
| 复购用户 | 历史已送达订单数 `>= 2` 的唯一购买用户 | 用户去重；复购率 = 复购用户 / 购买用户 |
| Cohort 留存率 | `active_customers / cohort_size` | cohort 为用户首购月；`cohort_index` 为距首购月的自然月差 |
| 平均配送天数 | `AVG(delivery_days)` | `delivery_days = delivered_customer_date - purchase_timestamp` |
| 延迟配送率 | `AVG(delivery_delay_days > 0)` | 订单级布尔值均值；展示时乘 100 转为百分比 |
| 品类分摊 GMV | 订单实付金额 / 订单商品件数，再按品类汇总 | 仅用于多商品订单的品类近似对比，非商品原始售价 GMV |

## 关键查询与验证

| 用途 | 文件/查询 | 复现说明 |
| --- | --- | --- |
| 月度经营健康度 | `sql/kpi_queries.sql` 查询 1 | 验证订单、GMV、客单价、配送时效趋势 |
| 用户复购率 | `sql/kpi_queries.sql` 查询 2 | 在用户级聚合后判断订单数是否至少为 2 |
| 支付方式表现 | `sql/kpi_queries.sql` 查询 3 | 对比支付方式的订单、GMV、客单价与配送时效 |
| 配送风险州 | `sql/kpi_queries.sql` 查询 4 | 仅保留至少 100 单的州，减少小样本误导 |
| Metabase 六张卡片 | `sql/metabase_questions.sql` | 与本地 Metabase 看板一一对应 |
| 看板渲染核验 | `docs/metabase_validation.md` | 记录数据源、卡片与本地渲染状态 |

## 本次校验基准

在已构建的 `data/analytics/ecommerce.db` 上执行：已送达订单量为 96,478，购买用户数为 93,358，GMV 为 15,422,461.77，客单价为 159.86，复购用户占比为 3.00%。月度 GMV 峰值出现在 2017-11，为 1,153,528.05。

## 图表快照

- `docs/screenshots/dashboard_overview.svg`：由订单宽表、月度指标、品类指标实时生成的经营、品类与配送风险图表。
- `docs/screenshots/cohort_retention.svg`：由 cohort 留存表生成的热力图。

以上为可复现的数据图表快照，不是经过人工修饰的业务成果图。重新下载数据后，依次运行 `python src/build_mart.py` 和 `python src/render_evidence.py` 即可重建。
