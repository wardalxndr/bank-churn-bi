# Data - real Bank Churn, no generator

## Source

Dataset asli: Churn Modelling (10,000 rows, target `Exited`), dari program
SuperDataScience dan tersebar luas di Kaggle. Repo ini mengambil salinan
publiknya lewat mirror GitHub:

`https://raw.githubusercontent.com/sharmaroshan/Churn-Modelling-Dataset/master/Churn_Modelling.csv`

Disimpan sebagai `data/bank_churn_raw.csv`. Sumber aslinya bisa dicek dari
judul dataset di atas kalau mau menulis sitasi di README utama.

## Recommended dataset

`Bank Customer Churn` - 10,000 rows, target `Exited` (1 = churn, 0 = stay).
Columns:
RowNumber, CustomerId, Surname, CreditScore, Geography, Gender, Age,
Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember,
EstimatedSalary, Exited

Why this one:
- Real, small enough for laptop, big enough for cohort + drivers
- Maps to Anabatic card lifecycle: HasCrCard + IsActiveMember = activation,
  Tenure + Balance + NumOfProducts = usage, Exited = churn/dormant
- Less pasaran than Telco (every tutorial uses Telco)

## Steps

1. Put the CSV at `data/bank_churn_raw.csv`
2. Do not commit the raw CSV (see .gitignore)
3. Run `python pipeline/build_marts.py` -> 3 marts + `save_list.xlsx`
4. Run `python pipeline/stats.py` -> numbers for the memo

## Card lifecycle mapping (for README + interview story)

- issued: row exists (CustomerId created)
- activated: HasCrCard = 1
- active: IsActiveMember = 1
- dormant risk: IsActiveMember = 0 but Exited = 0 (will churn soon)
- churn: Exited = 1
