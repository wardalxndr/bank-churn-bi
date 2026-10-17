"""Export one xlsx with 3 tabs so Looker Studio can read all marts from a single file.
Import this file into Google Sheets, then connect Looker Studio to that sheet.
Run: python pipeline/export_pack.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "dashboard_pack.xlsx"
TABS = ["mart_customer", "mart_cohort", "save_list"]


def main():
    frames = {}
    for name in TABS:
        path = ROOT / "data" / f"{name}.csv"
        if not path.exists():
            raise SystemExit(f"missing {path}. Run pipeline/build_marts.py first.")
        frames[name] = pd.read_csv(path)
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        for name, df in frames.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
    print(f"OK {OUT}")
    for name, df in frames.items():
        print(f"  tab {name}: {len(df)} rows, {len(df.columns)} cols")


if __name__ == "__main__":
    main()
