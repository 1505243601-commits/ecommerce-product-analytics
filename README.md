# 电商用户行为、复购与配送体验分析

面向数据分析实习的独立作品项目。项目使用 Olist Brazilian E-Commerce 的公开匿名数据，围绕订单增长、复购、品类表现与配送体验构建可复现的分析流程。

## 成果速览

| 分析维度 | 已验证结果 / 交付 |
| --- | --- |
| 数据范围 | 2016-09 至 2018-08 的公开历史样本，筛选已送达订单 |
| 数据规模 | **96,478 笔订单、93,358 名购买用户** |
| 用户复购 | **复购率 3.00%**；按用户唯一标识聚合，至少 2 笔已送达订单视为复购 |
| 月度趋势 | **2017-11 为 GMV 峰值月份** |
| BI 展示 | 经营概览、月度趋势、复购、Cohort、品类、配送风险 **6 张 Metabase 分析卡片** |
| 可复现交付 | 指标口径、SQL、图表快照与 Python 复现脚本 |

## 核心工作

- **数据建模：** 清洗并关联订单、支付、商品与用户数据，构建订单粒度宽表，以及月度、品类、Cohort 留存分析表。
- **经营分析：** 使用 SQL 定义 GMV、客单价、复购率与配送延迟率，识别月度销售峰值及用户复购表现。
- **风险定位：** 按州级配送延迟率与配送时长定位优先排查区域；州级查询仅保留至少 100 单的州。
- **成果复现：** 用 Metabase 展示指标，将指标定义、关键查询和图表快照与复现脚本一并归档。

以上为公开历史样本分析结果；未进行真实运营干预，不将分析发现表述为营收增长、复购提升或配送改善。

## 项目问题

1. 月度订单、GMV、客单价和活跃用户如何变化？
2. 用户首购后是否复购，留存表现如何？
3. 哪些品类、地区与支付方式贡献了订单和收入？
4. 配送时长和预计送达偏差是否与低评分有关？

## 技术栈

`SQL`、`Python`、`Pandas`、`SQLite`、`Power BI` / `Metabase`。

## 数据来源与边界

- 数据：Kaggle 的 [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)。
- 数据为公开、匿名化的历史订单数据，不代表任何项目方的真实业务。
- 不将分析建议写成已经带来业务提升；所有数值结论必须由本项目生成的结果文件支持。

## 快速开始

1. 从上述数据集下载并解压 CSV 到 `data/raw/`。
2. 安装依赖：`python -m pip install -r requirements.txt`。
3. 构建订单粒度分析宽表与汇总表：`python src/build_mart.py`。
4. 用任意 SQLite 客户端打开 `data/analytics/ecommerce.db`，执行 `sql/kpi_queries.sql`。
5. 将 `data/analytics/` 下的 CSV 导入 Power BI 或 Metabase，按 `docs/dashboard_spec.md` 制作看板。

## 产出

- `data/analytics/fact_orders.csv`：订单粒度分析宽表。
- `data/analytics/monthly_kpi.csv`：月度经营指标。
- `data/analytics/cohort_retention.csv`：用户首购 cohort 留存表。
- `data/analytics/category_kpi.csv`：品类经营表现。
- `data/analytics/ecommerce.db`：供 SQL 查询和 BI 工具连接的 SQLite 数据库。
- `docs/metabase_validation.md`：本地 Metabase 看板的卡片清单与渲染验证记录。

## 复现证据

- 指标口径、数据范围与核心结果校验：[指标口径与复现证据](docs/metric_definitions.md)
- 可复现图表快照：[经营、品类与配送风险](docs/screenshots/dashboard_overview.svg)、[Cohort 留存](docs/screenshots/cohort_retention.svg)
- 生成命令：先运行 `python src/build_mart.py`，再运行 `python src/render_evidence.py`。

![经营、品类与配送风险快照](docs/screenshots/dashboard_overview.svg)

![Cohort 留存快照](docs/screenshots/cohort_retention.svg)

## 延伸案例

- [AI 产品运营分析与埋点体系建设](ai_product_analytics/README.md)：使用匿名合成事件数据展示埋点字典、漏斗分析、数据质量校验和 BI 看板设计；不包含任何公司业务数据。
