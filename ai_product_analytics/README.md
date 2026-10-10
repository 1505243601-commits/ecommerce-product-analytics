# AI 产品运营分析与埋点体系建设

面向 AI 产品运营场景的可复现数据分析案例。以“访问产品 → 提交 Prompt → 成功生成 → 结果采纳”为主路径，完成埋点方案、漏斗指标、功能使用分析和看板设计。

> 数据边界：仓库中的事件数据由脚本生成，为**匿名合成样例**，仅用于展示分析方法、SQL 与数据质量校验流程；不包含或映射任何公司、用户或业务指标。

## 分析问题

1. 用户在生成链路的各阶段转化如何？
2. 哪些功能、端和模型版本的使用更活跃？
3. 埋点数据是否存在事件缺失、属性缺失或重复上报？
4. 运营看板应如何支持周度复盘与异常定位？

## 技术栈

`Python`、`Pandas`、`SQL`、埋点设计、用户行为漏斗、数据质量校验、`Metabase / Power BI`。

## 目录

```text
ai_product_analytics/
├── data/sample_events.csv          # 由脚本生成的匿名合成事件
├── data/analytics/                 # 漏斗与功能指标产出
├── docs/tracking_plan.md            # 事件与属性口径、验收规则
├── docs/dashboard_spec.md           # BI 看板设计
├── sql/funnel_metrics.sql           # 漏斗分析 SQL
└── src/
    ├── generate_sample_events.py    # 可复现的合成事件生成脚本
    └── build_metrics.py             # 指标和质量核查脚本
```

## 快速开始

```bash
python ai_product_analytics/src/generate_sample_events.py
python ai_product_analytics/src/build_metrics.py
```

运行后会在 `data/analytics/` 生成：

- `daily_funnel.csv`：按日漏斗人数与转化率；
- `feature_usage.csv`：功能、端、模型版本的使用汇总；
- `data_quality_checks.csv`：事件、关键属性和重复上报校验结果。


