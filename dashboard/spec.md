# Dashboard spec - 1 page executive (Looker Studio / Power BI)

## Top: KPI (4 cards)
- Total customers, churned, churn rate, save list size
- Source: reports/metrics.json + mart_customer

## Middle: trends + drivers
- Bar: churn rate by tenure bucket (0-2, 3-5, 6+)
- Bar: churn rate by IsActiveMember, by NumOfProducts, by Geography
- Table: top 10 reasons (inactive+single_product etc.)

## Bottom: action
- Table: save_list Top 100 (CustomerId, risk, reason, Geography)
- Filters: Geography, Tenure bucket
- Button: Export CSV/XLSX (uses data/save_list.xlsx)

## Excel spec
- Sheet 1: save_list (from pipeline)
- Sheet 2: pivot churn rate by Geography x Tenure
- Analyst can filter manually without code
