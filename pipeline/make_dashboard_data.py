"""Build data/dashboard_data.json consumed by dashboard/app.py.

One small JSON file so the dashboard runs anywhere (laptop or Streamlit
Cloud) without the gitignored 10k-row CSVs. Customer rows are the public
Kaggle churn dataset, no personal identifiers (CustomerId kept in save
list only for the action table).
Run: python pipeline/make_dashboard_data.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "dashboard_data.json"

CUSTOMER = ROOT / "data" / "mart_customer.csv"
COHORT = ROOT / "data" / "mart_cohort.csv"
SAVE = ROOT / "data" / "save_list.csv"

SAVE_COLS = ["CustomerId", "Geography", "Age", "Tenure", "Balance",
             "NumOfProducts", "risk", "reason"]
KEEP = ["Geography", "Gender", "Age", "Tenure", "Balance",
        "NumOfProducts", "HasCrCard", "IsActiveMember", "CreditScore",
        "EstimatedSalary", "Exited", "risk"]

TENURE_BUCKET = {"0-2": (0, 2), "3-5": (3, 5), "6+": (6, 10_000)}


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def bucket_for(tenure):
    for name, (lo, hi) in TENURE_BUCKET.items():
        if lo <= tenure <= hi:
            return name
    return "6+"


def customer_rows():
    rows = []
    for r in read_rows(CUSTOMER):
        tenure = int(float(r["Tenure"]))
        rows.append({
            "Geography": r["Geography"],
            "Age": int(float(r["Age"])),
            "Tenure": tenure,
            "Balance": round(float(r["Balance"]), 2),
            "NumOfProducts": int(float(r["NumOfProducts"])),
            "IsActiveMember": int(float(r["IsActiveMember"])),
            "Exited": int(float(r["Exited"])),
            "risk": int(r["risk"]),
            "tenure_bucket": bucket_for(tenure),
        })
    return rows


def save_rows():
    rows = []
    for r in read_rows(SAVE):
        rows.append({
            k: (float(r[k]) if k == "Balance" else
                int(r[k]) if k in ("Age", "Tenure", "NumOfProducts", "risk")
                else r[k])
            for k in SAVE_COLS
        })
    return rows


def reasons_bucket(save):
    by = defaultdict(int)
    for r in save:
        by[r["reason"]] += 1
    return sorted(by.items(), key=lambda x: -x[1])[:5]


def main():
    for p in (CUSTOMER, COHORT, SAVE):
        assert p.exists(), f"missing {p}. Run pipeline/build_marts.py first."
    customers = customer_rows()
    save = save_rows()
    churn = sum(r["Exited"] for r in customers)
    total = len(customers)
    cohort = {r["tenure_bucket"]: float(r["churn_rate"]) for r in read_rows(COHORT)}
    payload = {
        "kpis": {
            "total": total,
            "churn": churn,
            "churn_rate": round(churn / total, 4),
            "save_list": len(save),
            "save_risk_ge8": sum(1 for r in save if r["risk"] >= 8),
        },
        "tenure_chart": [[b, cohort[b]] for b in ("0-2", "3-5", "6+")],
        "reasons_snapshot": reasons_bucket(save),
        "customers": customers,
        "save_list": save,
    }
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"OK {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
