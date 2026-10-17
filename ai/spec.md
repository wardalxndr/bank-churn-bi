# AI spec (week 2) - Text to SQL over marts, grounded

## Scope
- Only answer from 3 marts. Outside marts -> say don't know.
- Input: Bahasa Indonesia, e.g. "nasabah churn paling banyak dari mana"
- Output: number + SQL used + 5 sample rows

## Guardrails
- Allowlist tables: mart_customer, mart_cohort, save_list
- Limit 500 rows, read-only queries only
- Log every Q + SQL + rows to reports/qa_log.csv

## Eval (like Wortschatz: 20 gold questions)
- 20 Q with expected SQL pattern + expected number range
- Metric: hit@1 (SQL matches) + number match tolerance 5%
- Target: document honestly in reports/qa_eval.json

## App
- `ai/app.py` Streamlit: text box -> generated SQL -> run BigQuery/CSV -> chart + table + download
- Model: Groq, retrieval: MinSearch over memo + schema docs
