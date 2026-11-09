-- Q4 conversion by device category (a user can appear under more than one device)
SELECT device.category AS device,
  COUNT(DISTINCT user_pseudo_id) AS users,
  COUNT(DISTINCT IF(event_name='add_to_cart', user_pseudo_id, NULL)) AS cart_users,
  COUNT(DISTINCT IF(event_name='begin_checkout', user_pseudo_id, NULL)) AS checkout_users,
  COUNT(DISTINCT IF(event_name='purchase', user_pseudo_id, NULL)) AS purchasers,
  ROUND(SUM(IF(event_name='purchase', ecommerce.purchase_revenue_in_usd, 0)),0) AS revenue_usd
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
GROUP BY device ORDER BY users DESC
