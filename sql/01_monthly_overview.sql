-- Q1 monthly overview
SELECT SUBSTR(event_date,1,6) AS month,
  COUNT(DISTINCT user_pseudo_id) AS users,
  COUNT(DISTINCT CONCAT(user_pseudo_id, CAST((SELECT value.int_value FROM UNNEST(event_params) WHERE key='ga_session_id') AS STRING))) AS sessions,
  COUNTIF(event_name='purchase') AS purchase_events,
  COUNT(DISTINCT IF(event_name='purchase', ecommerce.transaction_id, NULL)) AS transactions,
  ROUND(SUM(IF(event_name='purchase', ecommerce.purchase_revenue_in_usd, 0)),2) AS revenue_usd
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
GROUP BY month ORDER BY month
