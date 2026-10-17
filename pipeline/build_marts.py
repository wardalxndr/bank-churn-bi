"""Build 3 marts + Excel export from real Bank Churn CSV.
Input: data/bank_churn_raw.csv (Kaggle Bank Customer Churn, target Exited).
Outputs: mart_customer, mart_cohort, save_list (+ .xlsx for analysts).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

RAW = Path("data/bank_churn_raw.csv")
OUT_CUSTOMER = Path("data/mart_customer.csv")
OUT_COHORT = Path("data/mart_cohort.csv")
OUT_SAVE = Path("data/save_list.csv")
OUT_XLSX = Path("data/save_list.xlsx")
OUT_METRICS = Path("reports/metrics.json")


def load():
    rows = list(csv.DictReader(RAW.open(newline="", encoding="utf-8-sig")))
    # normalize: strip spaces, keep only needed cols with safe defaults
    clean = []
    for r in rows:
        try:
            clean.append({
                "CustomerId": r.get("CustomerId", "").strip(),
                "Geography": r.get("Geography", "Unknown").strip() or "Unknown",
                "Gender": r.get("Gender", "Unknown").strip() or "Unknown",
                "Age": int(float(r.get("Age", 0) or 0)),
                "Tenure": int(float(r.get("Tenure", 0) or 0)),
                "Balance": float(r.get("Balance", 0) or 0),
                "NumOfProducts": int(float(r.get("NumOfProducts", 0) or 0)),
                "HasCrCard": int(float(r.get("HasCrCard", 0) or 0)),
                "IsActiveMember": int(float(r.get("IsActiveMember", 0) or 0)),
                "CreditScore": int(float(r.get("CreditScore", 0) or 0)),
                "EstimatedSalary": float(r.get("EstimatedSalary", 0) or 0),
                "Exited": int(float(r.get("Exited", 0) or 0)),
            })
        except (ValueError, TypeError):
            continue
    return clean


def lifecycle(r):
    if r["Exited"] == 1:
        return "churn"
    if r["IsActiveMember"] == 0:
        return "dormant_risk"
    if r["HasCrCard"] == 1:
        return "active"
    return "issued"


def risk_score(r):
    # simple, explainable 0-10: mirrors QRIS weighting style
    s = 0
    if r["IsActiveMember"] == 0:
        s += 4
    if r["NumOfProducts"] == 1:
        s += 2
    if r["Tenure"] <= 2:
        s += 2
    if r["Age"] >= 55 or r["CreditScore"] < 550:
        s += 1
    if r["Balance"] == 0:
        s += 1
    return min(s, 10)


def reason(r):
    rs = []
    if r["IsActiveMember"] == 0:
        rs.append("inactive")
    if r["NumOfProducts"] == 1:
        rs.append("single_product")
    if r["Tenure"] <= 2:
        rs.append("new_tenure")
    if r["Balance"] == 0:
        rs.append("zero_balance")
    return "+".join(rs) if rs else "healthy"


def main():
    assert RAW.exists(), f"missing {RAW}, see data/README.md"
    rows = load()
    for r in rows:
        r["lifecycle"] = lifecycle(r)
        r["risk"] = risk_score(r)
        r["reason"] = reason(r)

    with OUT_CUSTOMER.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # cohort: by Tenure bucket
    coh = defaultdict(lambda: [0, 0])
    for r in rows:
        bucket = "0-2" if r["Tenure"] <= 2 else ("3-5" if r["Tenure"] <= 5 else "6+")
        coh[bucket][1] += 1
        coh[bucket][0] += r["Exited"]
    with OUT_COHORT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tenure_bucket", "churned", "total", "churn_rate"])
        for b in ["0-2", "3-5", "6+"]:
            c, t = coh.get(b, [0, 0])
            w.writerow([b, c, t, round(c / max(t, 1), 4)])

    # save list: dormant_risk sorted by risk desc, top 500
    save = [r for r in rows if r["lifecycle"] == "dormant_risk"]
    save.sort(key=lambda x: -x["risk"])
    save = save[:500]
    with OUT_SAVE.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["CustomerId", "Geography", "Age", "Tenure",
                                          "Balance", "NumOfProducts", "risk", "reason"])
        w.writeheader()
        for r in save:
            w.writerow({k: r[k] for k in w.fieldnames})

    try:
        import pandas as pd
        pd.DataFrame(save).to_excel(OUT_XLSX, index=False)
        xlsx = True
    except ImportError:
        xlsx = False

    total = len(rows)
    churn = sum(r["Exited"] for r in rows)
    OUT_METRICS.parent.mkdir(exist_ok=True)
    json.dump({"total": total, "churn": churn,
               "churn_rate": round(churn / max(total, 1), 4),
               "save_list": len(save), "xlsx": xlsx},
              open(OUT_METRICS, "w"), indent=2)
    print(f"OK total={total} churn={churn} save={len(save)} xlsx={xlsx}")


if __name__ == "__main__":
    main()
