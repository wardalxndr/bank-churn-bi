# Digital Subscription Churn BI - Card Lifecycle Edition

BI project for bank card lifecycle: issued -> activated -> active -> dormant -> churn.
Built for Anabatic-style clients: bank digital, multifinance, CX.

## Why not pasaran

Most churn projects stop at churn rate chart from Telco data.
This one outputs a save list with reason per customer plus SQL proof,
Excel export for analysts, and Text-to-SQL Q&A with eval.

## Stack

Python + BigQuery + dbt (marts), Looker + Excel (dashboard),
Streamlit + Groq + MinSearch (AI Q&A), Kestra daily (automation).

## Quickstart

1. `pip install -r requirements.txt`
2. Data: `data/bank_churn_raw.csv` (Kaggle Bank Customer Churn, see `data/README.md`)
3. `python pipeline/build_marts.py` -> 3 marts + `save_list.xlsx`
4. `python pipeline/stats.py` -> numbers for the memo (`reports/stats.json`)
5. Decision dashboard (Streamlit): `streamlit run dashboard/app.py` -> verdict
   callout + KPI + geo + product mix + worklist 500 sorted by risk.
   `data/dashboard_data.json` is committed, so it runs out of the box;
   rebuild it with `python pipeline/make_dashboard_data.py`.
6. Dashboard in Looker Studio: `python pipeline/export_pack.py` ->
   `data/dashboard_pack.xlsx`, then follow `dashboard/build_guide.md`
   (Looker Studio via Google Sheets)
7. AI Q&A: set `GROQ_API_KEY`, then `streamlit run ai/app.py` (run from repo root).
   Model default `openai/gpt-oss-120b`; ganti kapan saja lewat `GROQ_MODEL` kalau
   Groq pensiunin modelnya.

## Results (verified on the real dataset, 10K rows)

- Churn rate 20.37% overall, 2037 churned
- Germany leaks most: 32.44% vs France 16.15% / Spain 16.67%
- Inactive customers churn 26.85% vs active 14.27%
- 4 products = 100% churn (60 rows), 1 product = 27.71%
- Save list: 500 dormant risk customers, 437 with risk >= 8
- Top reason: inactive + single product + new tenure (300 of 500)

## Status

- [x] marts + hero queries + dashboard specs
- [x] verified pipeline + stats (`reports/stats.json`)
- [x] Text-to-SQL demo with guardrails + 20 gold questions (`ai/`)
- [x] dashboard build guide + one file import pack (`dashboard/`)
- [x] decision-first Streamlit dashboard: verdict + worklist 500 (`dashboard/app.py`)
- [ ] Looker dashboard live link (next)
- [ ] AI eval scores written to `reports/qa_eval.json` (next)

## Layout

- `data/` raw + marts output (gitignored CSVs, committed README)
- `sql/` 3 hero queries: cohort churn, drivers, save list
- `pipeline/` mart builder + dashboard data pack + Excel export + stats
- `dashboard/` Streamlit 1-page app (`app.py`) + Looker build guide + pivot spec
- `ai/` Text-to-SQL app (core + streamlit), spec, 20 gold questions
- `reports/` metrics + stats + memos
