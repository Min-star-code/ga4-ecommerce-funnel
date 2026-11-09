-- Q5 data quality checks on purchase events and traffic fields
SELECT
  COUNTIF(event_name='purchase') AS purchase_events,
  COUNTIF(event_name='purchase' AND (ecommerce.transaction_id IS NULL OR ecommerce.transaction_id='(not set)')) AS purchase_no_txn_id,
  COUNT(DISTINCT IF(event_name='purchase' AND ecommerce.transaction_id!='(not set)', ecommerce.transaction_id, NULL)) AS distinct_txn_ids,
  COUNTIF(event_name='purchase' AND (ecommerce.purchase_revenue_in_usd IS NULL OR ecommerce.purchase_revenue_in_usd=0)) AS purchase_zero_revenue,
  COUNT(DISTINCT user_pseudo_id) AS users,
  COUNT(DISTINCT IF(traffic_source.medium IN ('<Other>','(data deleted)'), user_pseudo_id, NULL)) AS users_obfuscated_medium,
  COUNT(DISTINCT IF(traffic_source.medium='(none)', user_pseudo_id, NULL)) AS users_direct
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
