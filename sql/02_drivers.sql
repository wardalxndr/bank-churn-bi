-- 02: drivers - what separates churn vs stay
SELECT
  IsActiveMember,
  COUNT(*) AS total,
  SUM(Exited) AS churned,
  ROUND(AVG(Exited), 4) AS churn_rate,
  ROUND(AVG(CreditScore), 1) AS avg_score,
  ROUND(AVG(Balance), 1) AS avg_balance
FROM bank_churn_raw
GROUP BY 1
ORDER BY 1;

-- swap dimension: Geography, Gender, HasCrCard, NumOfProducts
