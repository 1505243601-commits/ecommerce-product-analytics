# 埋点方案与验收规则

## 事件字典

| 事件 | 触发时机 | 用途 | 必填属性 |
| --- | --- | --- | --- |
| `page_view` | 用户进入 AI 功能页 | 访问用户、会话基数 | `event_date`、`user_id`、`session_id`、`platform` |
| `prompt_submit` | 用户提交 Prompt | 输入意愿与生成入口转化 | `feature`、`model_version` |
| `generation_success` | 服务返回可展示结果 | 生成成功率与模型使用 | `feature`、`model_version` |
| `result_adopt` | 用户复制、保存或插入结果 | 结果采纳与价值行为 | `feature`、`model_version` |
| `feature_click` | 用户点击辅助功能 | 功能渗透率 | `feature`、`platform` |

## 核心指标口径

- **提交率** = 当日 `prompt_submit` 去重用户数 / 当日 `page_view` 去重用户数。
- **生成成功率** = 当日 `generation_success` 去重用户数 / 当日 `prompt_submit` 去重用户数。
- **结果采纳率** = 当日 `result_adopt` 去重用户数 / 当日 `generation_success` 去重用户数。
- **功能使用用户数** = 按 `feature`、`platform`、`model_version` 分组后的 `feature_click` 去重用户数。

## 验收与质量校验

1. 对照事件字典检查事件名是否在允许集合内。
2. 检查各事件的关键属性缺失率；缺失记录需回传埋点或数据开发负责人排查。
3. 以 `event_date + user_id + session_id + event_name + feature` 检查重复上报。
4. 检查漏斗顺序是否合理：同一用户在同日应先发生 `page_view`，再发生后续生成链路事件。
5. 发布或改版后，以抽样日志与前端实际操作交叉验证埋点触发时机。
