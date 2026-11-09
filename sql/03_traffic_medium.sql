-- Q3 conversion by traffic medium, one medium per user.
-- traffic_source can differ across a user's events in this sample, so each user is
-- assigned the medium recorded on their earliest event.
WITH user_medium AS (
  SELECT user_pseudo_id,
    ARRAY_AGG(traffic_source.medium ORDER BY event_timestamp LIMIT 1)[OFFSET(0)] AS medium
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  GROUP BY user_pseudo_id
),
user_actions AS (
  SELECT user_pseudo_id,
    MAX(IF(event_name='add_to_cart', 1, 0)) AS carted,
    MAX(IF(event_name='purchase', 1, 0)) AS purchased,
    SUM(IF(event_name='purchase', ecommerce.purchase_revenue_in_usd, 0)) AS revenue
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  GROUP BY user_pseudo_id
)
SELECT m.medium,
  COUNT(*) AS users,
  SUM(a.carted) AS cart_users,
  SUM(a.purchased) AS purchasers,
  ROUND(SUM(a.revenue), 0) AS revenue_usd
FROM user_medium m JOIN user_actions a USING (user_pseudo_id)
GROUP BY m.medium ORDER BY users DESC
