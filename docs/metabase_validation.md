# Metabase 本地看板验证记录

## 实例与数据源

- 本地 Metabase 使用 SQLite 数据库 `data/analytics/ecommerce.db`。
- 仪表板名称：`E-commerce Behavior, Retention and Delivery Analysis`。
- 数据源为公开匿名化的 Olist 历史电商数据；不要将其解读为当前真实业务数据。

## 已创建的问题卡

1. `Executive KPI`：已送达订单、购买用户、GMV、客单价、延迟配送率。
2. `Monthly GMV and Orders`：月度订单、GMV 与客单价趋势。
3. `Customer Repeat Purchase`：一次购买与复购用户占比。
4. `Cohort Retention`：按首购月份与复购月序的留存明细。
5. `Top Category Performance`：按分摊 GMV 排序的头部品类。
6. `Delivery Risk States`：订单量不少于 100 的州级配送风险。

## 验证结果

- 六张问题卡均已写入仪表板并在本地浏览器渲染。
- 月度趋势、复购占比、品类表现和配送风险均返回结果；cohort 留存当前以表格展示。
- `Executive KPI` 使用单值可视化时只突出显示首个指标（96,478 笔已送达订单）；其余 KPI 可在问题卡结果中查看。若用于正式展示，建议将其拆成 5 个独立数字卡。

## 下一步优化

- 将 Cohort Retention 配置为矩阵/热力图。
- 将 Executive KPI 拆分为订单量、购买用户、GMV、客单价、延迟配送率五张数字卡。
- 在实际 Metabase 环境中导出图表截图，并在 README 中补充图片链接。
