"""Core for the Text to SQL demo. No streamlit import here so it can be tested headless.
Loads the 3 marts into in-memory SQLite, generates SQL via Groq, runs with guardrails.
"""
import csv
import os
import re
import sqlite3
import threading
from pathlib import Path

_DB_LOCK = threading.Lock()

ROOT = Path(__file__).resolve().parents[1]
QA_LOG = ROOT / "reports" / "qa_log.csv"

MART_FILES = {
    "mart_customer": "data/mart_customer.csv",
    "mart_cohort": "data/mart_cohort.csv",
    "save_list": "data/save_list.csv",
}

INT_COLS = {"Age", "Tenure", "NumOfProducts", "HasCrCard", "IsActiveMember",
            "CreditScore", "Exited", "risk", "churned", "total"}
REAL_COLS = {"Balance", "EstimatedSalary", "churn_rate"}

SCHEMA_DOC = """
mart_customer(CustomerId TEXT, Geography TEXT, Gender TEXT, Age INTEGER, Tenure INTEGER,
  Balance REAL, NumOfProducts INTEGER, HasCrCard INTEGER, IsActiveMember INTEGER,
  CreditScore INTEGER, EstimatedSalary REAL, Exited INTEGER, lifecycle TEXT, risk INTEGER, reason TEXT)
  note: Exited 1 = churn, 0 = stay. lifecycle in (active, dormant_risk, issued, churn). risk 0 to 10.
mart_cohort(tenure_bucket TEXT, churned INTEGER, total INTEGER, churn_rate REAL)
  note: tenure_bucket in ('0-2', '3-5', '6+').
save_list(CustomerId TEXT, Geography TEXT, Age INTEGER, Tenure INTEGER, Balance REAL,
  NumOfProducts INTEGER, risk INTEGER, reason TEXT)
  note: top 500 dormant_risk customers sorted by risk desc. reason like 'inactive+single_product'.
"""


def col_type(name):
    if name in INT_COLS:
        return "INTEGER"
    if name in REAL_COLS:
        return "REAL"
    return "TEXT"


def load_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    for table, rel in MART_FILES.items():
        path = ROOT / rel
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            raise SystemExit(f"empty mart: {path}. Run pipeline/build_marts.py first.")
        cols = list(rows[0].keys())
        ddl = ", ".join(f"{c} {col_type(c)}" for c in cols)
        conn.execute(f"CREATE TABLE {table} ({ddl})")
        marks = ", ".join("?" for _ in cols)
        conn.executemany(f"INSERT INTO {table} VALUES ({marks})",
                         [[r[c] for c in cols] for r in rows])
    conn.commit()
    return conn


ALLOWED_TABLES = set(MART_FILES)
BLOCKED = ("insert", "update", "delete", "drop", "alter", "attach", "pragma", "create")


def run_sql(conn, sql, max_rows=500):
    s = sql.strip().rstrip(";")
    low = " ".join(s.lower().split())
    if not low.startswith("select"):
        raise ValueError("hanya SELECT yang boleh")
    for bad in BLOCKED:
        if re.search(rf"\b{bad}\b", low):
            raise ValueError(f"kata terlarang: {bad}")
    used = set(re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)", low))
    unknown = used - ALLOWED_TABLES
    if unknown:
        raise ValueError(f"tabel tidak boleh: {', '.join(sorted(unknown))}")
    if "limit" not in low:
        s += f" LIMIT {max_rows}"
    with _DB_LOCK:
        cur = conn.execute(s)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return cols, rows


def build_prompt(question):
    return (
        "You are a BI assistant for a bank churn project. "
        "Translate the question into ONE SQLite SELECT query. "
        "Use only the tables and columns below, never invent names. "
        "Reply with SQL only, no markdown, no explanation.\n"
        f"Tables:\n{SCHEMA_DOC}\n"
        f"Question: {question}"
    )


def gen_sql(question, model=None):
    from groq import Groq
    model = model or os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=model, temperature=0,
        messages=[{"role": "user", "content": build_prompt(question)}],
    )
    sql = resp.choices[0].message.content.strip()
    return sql.replace("```sql", "").replace("```", "").strip()


def log_qa(question, sql, n_rows):
    import datetime
    QA_LOG.parent.mkdir(exist_ok=True)
    new = not QA_LOG.exists()
    with open(QA_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "question", "sql", "n_rows"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"),
                    question, " ".join(sql.split()), n_rows])
