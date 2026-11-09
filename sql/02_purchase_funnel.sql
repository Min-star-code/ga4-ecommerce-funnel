-- Q2 user-level purchase funnel: users who reached each step at least once
SELECT
  COUNT(DISTINCT user_pseudo_id) AS all_users,
  COUNT(DISTINCT IF(event_name='view_item', user_pseudo_id, NULL)) AS view_item,
  COUNT(DISTINCT IF(event_name='add_to_cart', user_pseudo_id, NULL)) AS add_to_cart,
  COUNT(DISTINCT IF(event_name='begin_checkout', user_pseudo_id, NULL)) AS begin_checkout,
  COUNT(DISTINCT IF(event_name='add_shipping_info', user_pseudo_id, NULL)) AS add_shipping_info,
  COUNT(DISTINCT IF(event_name='add_payment_info', user_pseudo_id, NULL)) AS add_payment_info,
  COUNT(DISTINCT IF(event_name='purchase', user_pseudo_id, NULL)) AS purchase
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
