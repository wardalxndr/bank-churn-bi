-- 01: churn daily proxy (by Tenure bucket, since no date in raw)
-- Hero query 1 for README + interview demo
SELECT
  CASE
    WHEN Tenure <= 2 THEN '0-2'
    WHEN Tenure <= 5 THEN '3-5'
    ELSE '6+'
  END AS tenure_bucket,
  COUNT(*) AS total,
  SUM(Exited) AS churned,
  ROUND(AVG(Exited), 4) AS churn_rate
FROM bank_churn_raw
GROUP BY 1
ORDER BY 1;
