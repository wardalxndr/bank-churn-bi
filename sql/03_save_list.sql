-- 03: save list - priority to call, with reason
-- Rule mirrors pipeline/build_marts.py so SQL and Python agree
SELECT
  CustomerId, Geography, Age, Tenure, Balance, NumOfProducts,
  (CASE WHEN IsActiveMember = 0 THEN 4 ELSE 0 END
   + CASE WHEN NumOfProducts = 1 THEN 2 ELSE 0 END
   + CASE WHEN Tenure <= 2 THEN 2 ELSE 0 END
   + CASE WHEN CreditScore < 550 OR Age >= 55 THEN 1 ELSE 0 END
   + CASE WHEN Balance = 0 THEN 1 ELSE 0 END) AS risk,
  CONCAT_WS('+',
    IF(IsActiveMember = 0, 'inactive', NULL),
    IF(NumOfProducts = 1, 'single_product', NULL),
    IF(Tenure <= 2, 'new_tenure', NULL),
    IF(Balance = 0, 'zero_balance', NULL)) AS reason
FROM bank_churn_raw
WHERE Exited = 0 AND IsActiveMember = 0
ORDER BY risk DESC
LIMIT 500;
