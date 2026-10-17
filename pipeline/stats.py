"""Print key numbers from marts: for memo + AI eval reference.
Run after build_marts.py: python pipeline/stats.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "stats.json"


def load(name):
    with open(ROOT / "data" / f"{name}.csv", newline="") as f:
        return list(csv.DictReader(f))


def rate(rows):
    return round(sum(int(r["Exited"]) for r in rows) / max(len(rows), 1), 4)


def t_bucket(t):
    t = int(t)
    if t <= 2:
        return "0-2"
    if t <= 5:
        return "3-5"
    return "6+"


def main():
    cust = load("mart_customer")
    save = load("save_list")
    act = [r for r in cust if r["IsActiveMember"] == "1"]
    inact = [r for r in cust if r["IsActiveMember"] == "0"]
    geo = {}
    for g in sorted({r["Geography"] for r in cust}):
        gro = [r for r in cust if r["Geography"] == g]
        geo[g] = {"n": len(gro), "churn_rate": rate(gro)}
    prod = {}
    for p in sorted({r["NumOfProducts"] for r in cust}):
        pro = [r for r in cust if r["NumOfProducts"] == p]
        prod[p] = {"n": len(pro), "churn_rate": rate(pro)}
    tenure = {}
    for b in ["0-2", "3-5", "6+"]:
        tro = [r for r in cust if t_bucket(r["Tenure"]) == b]
        tenure[b] = {"n": len(tro), "churn_rate": rate(tro)}
    churn_rows = [r for r in cust if r["Exited"] == "1"]
    stay_rows = [r for r in cust if r["Exited"] == "0"]
    out = {
        "total": len(cust),
        "churn": len(churn_rows),
        "churn_rate": rate(cust),
        "active": {"n": len(act), "churn_rate": rate(act)},
        "inactive": {"n": len(inact), "churn_rate": rate(inact)},
        "geo": geo,
        "products": prod,
        "tenure": tenure,
        "avg_age_churn": round(sum(int(r["Age"]) for r in churn_rows) / max(len(churn_rows), 1), 1),
        "avg_age_stay": round(sum(int(r["Age"]) for r in stay_rows) / max(len(stay_rows), 1), 1),
        "save_list": len(save),
        "save_reasons_top": Counter(r["reason"] for r in save).most_common(5),
        "save_risk_ge8": sum(1 for r in save if int(r["risk"]) >= 8),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
