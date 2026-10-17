"""Streamlit demo: ask in Indonesian, get SQL plus numbers plus table.
Run from repo root: streamlit run ai/app.py
Set GROQ_API_KEY first (see README).
"""
import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import gen_sql, load_db, log_qa, run_sql

st.set_page_config(page_title="Churn BI - Tanya Data", layout="wide")

st.title("Digital Subscription Churn BI")
st.caption("Tanya pakai bahasa Indonesia. Jawaban selalu dari SQL atas mart, bukan tebakan.")


@st.cache_resource
def db():
    return load_db()


conn = db()

EXAMPLES = [
    "Berapa churn rate keseluruhan?",
    "Churn rate per geography, urut dari tertinggi",
    "Churn rate nasabah inactive vs active",
    "Top 10 save list dengan risk tertinggi",
]

q = st.text_input("Pertanyaan", placeholder="contoh: churn rate per jumlah produk")
ask = st.button("Tanya", type="primary")

if ask and q:
    if not os.environ.get("GROQ_API_KEY"):
        st.error('Set GROQ_API_KEY dulu, contoh di PowerShell: $env:GROQ_API_KEY = "isi"')
        st.stop()
    with st.spinner("Menyusun SQL..."):
        try:
            sql = gen_sql(q)
        except Exception as e:
            st.error(f"Gagal manggil Groq: {e}")
            st.info("Kalau 404 model, cek daftar model aktif atau set GROQ_MODEL, "
                    "contoh: $env:GROQ_MODEL = \"openai/gpt-oss-120b\"")
            st.stop()
    st.code(sql, language="sql")
    try:
        cols, rows = run_sql(conn, sql)
        st.dataframe([dict(zip(cols, r)) for r in rows], use_container_width=True)
        st.caption(f"{len(rows)} baris")
        log_qa(q, sql, len(rows))
    except Exception as e:
        st.error(f"Query ditolak: {e}")

with st.expander("Contoh pertanyaan"):
    for e in EXAMPLES:
        st.write(f"- {e}")

with st.expander("Isi mart"):
    st.write("mart_customer: 1 baris per nasabah plus lifecycle dan risk")
    st.write("mart_cohort: churn rate per bucket tenure")
    st.write("save_list: 500 nasabah dormant risk prioritas")
