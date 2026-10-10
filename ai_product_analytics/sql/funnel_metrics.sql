-- 将 sample_events.csv 导入 events 表后执行。
-- 字段：event_date, user_id, session_id, event_name, feature, model_version, platform
WITH daily_users AS (
  SELECT
    event_date,
    COUNT(DISTINCT CASE WHEN event_name = 'page_view' THEN user_id END) AS view_users,
    COUNT(DISTINCT CASE WHEN event_name = 'prompt_submit' THEN user_id END) AS submit_users,
    COUNT(DISTINCT CASE WHEN event_name = 'generation_success' THEN user_id END) AS success_users,
    COUNT(DISTINCT CASE WHEN event_name = 'result_adopt' THEN user_id END) AS adopt_users
  FROM events
  GROUP BY event_date
)
SELECT
  event_date,
  view_users,
  submit_users,
  success_users,
  adopt_users,
  ROUND(1.0 * submit_users / NULLIF(view_users, 0), 4) AS submit_rate,
  ROUND(1.0 * success_users / NULLIF(submit_users, 0), 4) AS generation_success_rate,
  ROUND(1.0 * adopt_users / NULLIF(success_users, 0), 4) AS adoption_rate
FROM daily_users
ORDER BY event_date;
