"""One-page churn BI dashboard (Streamlit) - white/blue clean edition.

Run: streamlit run dashboard/app.py
Data: pipeline/make_dashboard_data.py -> data/dashboard_data.json
"""
import json
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path = __import__("pathlib").Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dashboard_data.json"

BLUE = "#2F6BF0"
RAMP = ["#2F6BF0", "#5B8DEF", "#8AB1F5", "#AFC9FA", "#C7DAFB"]
INK = "#17233D"
GREY = "#667085"
BORDER = "#E7ECF4"

st.set_page_config(layout="wide", page_title="Customer Churn Dashboard",
                   page_icon=":", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: INK; }
.stApp { background: #FFFFFF; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1620px; padding-top: .8rem; padding-bottom: 1.4rem; }

[data-testid="stSidebar"] { background: #F7F9FC; border-right: 1px solid BORDER; }
[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }

.app-name { font-size: 15px; font-weight: 700; color: INK; }
.logo-ic { display: inline-flex; width: 26px; height: 26px; border-radius: 8px;
  background: #EAF1FE; color: BLUE; align-items: center; justify-content: center;
  font-size: 14px; margin-right: 8px; }
.avatar { display: inline-flex; width: 32px; height: 32px; border-radius: 50%;
  background: BLUE; color: #fff; align-items: center; justify-content: center;
  font-weight: 700; font-size: 13px; }

.headline { font-size: 27px; font-weight: 700; color: INK; letter-spacing: -.2px; }
.subline { color: GREY; font-size: 13px; margin-bottom: 4px; }

.card, [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF;
  border: 1px solid BORDER !important; border-radius: 16px !important;
  box-shadow: 0 1px 3px rgba(23,35,61,.04); }
[data-testid="stVerticalBlockBorderWrapper"] { padding: 18px 22px 12px; }

.kpi { padding: 18px 20px; border: 1px solid BORDER; border-radius: 16px;
  background: #fff; box-shadow: 0 1px 3px rgba(23,35,61,.04); height: 100%; }
.kpi-flex { display: flex; align-items: flex-start; gap: 14px; }
.kpi-ic { flex: 0 0 auto; display: inline-flex; width: 40px; height: 40px;
  border-radius: 10px; background: #EAF1FE; color: BLUE;
  align-items: center; justify-content: center; font-size: 19px; }
.kpi-label { font-size: 11px; font-weight: 700; letter-spacing: 1px;
  text-transform: uppercase; color: GREY; }
.kpi-value { font-size: 33px; font-weight: 700; color: INK; line-height: 1.2; }
.kpi-note { font-size: 12px; color: GREY; margin-top: 1px; }

.callout { background: #EAF1FE; border: 1px solid #C7DAFB; border-radius: 12px;
  padding: 14px 20px; }
.callout-title { font-size: 13.5px; font-weight: 700; color: #1B44B8;
  letter-spacing: .2px; }
.callout-sub { font-size: 13px; color: #3D4A63; margin-top: 2px; }

.tile-title { font-size: 15px; font-weight: 700; color: INK; }
.tile-note { font-size: 12px; color: GREY; }
.cap { font-size: 12px; color: GREY; }

.pill { background: #F5F8FF; border: 1px solid #E3EAFB; border-radius: 10px;
  padding: 8px 12px; font-size: 12.5px; color: #44515F; }
.mrow { display: flex; align-items: center; justify-content: space-between;
  padding: 5px 0; font-size: 12.5px; color: INK; }
.mrow .n { color: GREY; }
.dot { display: inline-block; width: 11px; height: 11px; border-radius: 3px;
  margin-right: 8px; }

.worklist { max-height: 264px; overflow: auto; }
.worklist table { width: 100%; border-collapse: collapse; font-size: 13px; }
.worklist th { text-align: left; font-size: 10.5px; font-weight: 700;
  letter-spacing: .8px; text-transform: uppercase; color: GREY;
  border-bottom: 1px solid BORDER; padding: 7px 10px; position: sticky;
  top: 0; background: #fff; }
.worklist td { padding: 7px 10px; border-bottom: 1px solid #F1F4F9; color: INK; }
.chip { display: inline-block; min-width: 40px; text-align: center;
  padding: 3px 9px; border-radius: 8px; font-weight: 700; font-size: 12.5px;
  color: #1B44B8; }

.footer { color: GREY; font-size: 12px; }
div[data-baseweb="select"] > div { border-radius: 10px; }
button[kind="secondary"] { border-radius: 999px !important; }
</style>
""".replace("INK", INK).replace("GREY", GREY).replace(
    "BORDER", BORDER).replace("BLUE", BLUE)


def fmt_int(n):
    return f"{n:,}"


def fmt_pct(p, dec=1):
    return f"{p * 100:.{dec}f}%"


@st.cache_data
def load():
    with DATA.open(encoding="utf-8") as f:
        return json.load(f)


data = load()
snap = data["kpis"]
customers = pd.DataFrame(data["customers"])
save = pd.DataFrame(data["save_list"])

st.markdown(CSS, unsafe_allow_html=True)

gone = customers[customers["Exited"] == 1]
geo_rate = customers.groupby("Geography")["Exited"].mean().sort_values(
    ascending=False)
active_rate = customers.groupby("IsActiveMember")["Exited"].mean()
ten_rate = customers.groupby("tenure_bucket")["Exited"].mean()
prod_counts = gone["NumOfProducts"].value_counts().sort_index()
reasons = save["reason"].value_counts()

CHURNED = int(snap["churn"])
SAVE_N = int(snap["save_list"])
RISK8 = int(snap["save_risk_ge8"])
TOP_REASON, TOP_N = data["reasons_snapshot"][0]

reason_en = TOP_REASON.replace("_", " ")


# ---------- chart helpers ----------
def style_base(fig, height):
    fig.update_layout(
        height=height, margin=dict(l=6, r=6, t=10, b=6),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=GREY, size=12),
        dragmode=False)
    fig.update_xaxes(showline=True, linecolor=BORDER, tickfont=dict(size=12,
                     color=GREY))
    fig.update_yaxes(gridcolor="#F1F4F9", tickfont=dict(size=11, color=GREY))
    return fig


def col_chart():
    yes = float(active_rate[0])
    no = float(active_rate[1])
    fig = go.Figure(go.Bar(
        x=["Inactive", "Active"], y=[yes, no],
        marker_color=[RAMP[0], RAMP[3]],
        text=[fmt_pct(yes), fmt_pct(no)], textposition="outside",
        textfont=dict(size=14, color=INK, family="Inter, sans-serif"),
        cliponaxis=False, width=.5))
    style_base(fig, 250)
    fig.update_yaxes(range=[0, .42],
                     tickvals=[0, .1, .2, .3, .4],
                     ticktext=["0%", "10%", "20%", "30%", "40%"])
    fig.update_xaxes(showline=False)
    fig.update_layout(bargap=.45)
    return fig


def tenure_chart():
    order = {"0-2": 0, "3-5": 1, "6+": 2}
    pairs = sorted(ten_rate.items(), key=lambda x: order.get(x[0], 3))
    labels = [f"{b}y" for b, _ in pairs]
    vals = [float(r) for _, r in pairs]
    fig = go.Figure(go.Scatter(
        x=labels, y=vals, mode="lines+markers+text",
        line=dict(color=RAMP[0], width=2), marker=dict(size=8, color=RAMP[0]),
        text=[fmt_pct(v) for v in vals], textposition="top center",
        textfont=dict(size=13, color=INK, family="Inter, sans-serif"),
        cliponaxis=False))
    style_base(fig, 250)
    fig.update_yaxes(range=[.15, .26], tickvals=[.15, .2, .25],
                     ticktext=["15%", "20%", "25%"])
    fig.update_xaxes(showline=True, linecolor=BORDER)
    fig.update_layout(showlegend=False, margin=dict(t=30))
    return fig


def map_chart():
    iso = {"Germany": "DEU", "Spain": "ESP", "France": "FRA"}
    fig = go.Figure(go.Choropleth(
        locations=[iso[g] for g in geo_rate.index],
        z=[float(r) for r in geo_rate.values],
        text=list(geo_rate.index),
        colorscale=[[0, "#BFD5FB"], [1, "#2456CB"]],
        zmin=.1, zmax=.35, showscale=False,
        marker=dict(line=dict(color="#FFFFFF", width=1)),
        hovertemplate="%{text}: %{z:.1%}<extra></extra>"))
    fig.update_layout(
        height=360, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#EEF2F8",
                 showcountries=True, countrycolor="#FFFFFF",
                 showcoastlines=False, showframe=False, resolution=50,
                 projection=dict(type="natural earth", scale=3.6),
                 center=dict(lat=48.5, lon=2.5)))
    return fig


def donut_chart():
    labels = [f"{n} product{'s' if n > 1 else ''}" for n in prod_counts.index]
    vals = [int(v) for v in prod_counts.values]
    total = sum(vals)
    texts = [fmt_pct(v / total) if v / total >= .05 else "" for v in vals]
    fig = go.Figure(go.Pie(
        labels=labels, values=vals, hole=.66, sort=False, direction="clockwise",
        marker=dict(colors=[RAMP[0], RAMP[1], RAMP[2], RAMP[4]]),
        text=texts, textinfo="text", textposition="inside",
        insidetextorientation="horizontal", showlegend=False,
        hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>"))
    fig.add_annotation(
        text=f"<b style='font-size:21px;color:{INK}'>{fmt_int(total)}</b>"
             f"<br><span style='font-size:12px;color:{GREY}'>churned</span>",
        showarrow=False, font=dict(family="Inter, sans-serif"))
    fig.update_traces(textfont=dict(
        color=["#FFFFFF", INK, INK, INK], size=13,
        family="Inter, sans-serif"))
    fig.update_layout(height=300, margin=dict(l=4, r=4, t=4, b=4),
                      paper_bgcolor="rgba(0,0,0,0)")
    return fig


def reasons_chart():
    top5 = reasons.head(5)
    labels = [r.replace("_", " ").replace("single product", "single prod")
              for r in top5.index]
    vals = [int(v) for v in top5.values]
    pcts = [v / SAVE_N for v in vals]
    fig = go.Figure(go.Bar(
        y=labels, x=vals, orientation="h",
        marker_color=[RAMP[0], RAMP[0], RAMP[1], RAMP[2], RAMP[3]],
        text=[fmt_pct(p) for p in pcts], textposition="outside",
        textfont=dict(size=13, color=INK, family="Inter, sans-serif"),
        cliponaxis=False))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=252, margin=dict(l=8, r=56, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=GREY, size=12.5),
        xaxis=dict(visible=False), bargap=.42)
    return fig


def card_open():
    return st.container(border=True)


def tile_open(title, note=None, align_note=False):
    card_open()
    if note:
        h1, h2 = st.columns([.72, .28])
        h1.markdown(f'<div class="tile-title">{title}</div>',
                    unsafe_allow_html=True)
        h2.markdown(f'<div class="tile-note" style="text-align:right;'
                    f'margin-top:3px">{note}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="tile-title">{title}</div>',
                    unsafe_allow_html=True)


# ---------- sidebar nav ----------
with st.sidebar:
    st.markdown(f'<div class="app-name"><span class="logo-ic">🌀</span>'
                f'Customer Churn BI</div>', unsafe_allow_html=True)
    st.write("")
    nav = st.radio("Navigation",
                   ["Overview", "Customers", "Churn Analysis", "Products",
                    "Regions", "Reports"], label_visibility="collapsed")
    st.write("")
    st.caption("snapshot Oct 2026 (Kaggle, 10,000 rows)")

st.markdown(CSS, unsafe_allow_html=True)

if nav != "Overview":
    st.markdown(f'<div class="headline">{nav}</div>', unsafe_allow_html=True)
    st.info("Under construction. Overview is the live page of this demo.")
    st.stop()

# ---------- top bar ----------
tb1, tb2, tb3 = st.columns([.68, .18, .14])
tb1.markdown('<div class="app-name" style="font-size:16px">'
             'Customer Churn Dashboard</div>', unsafe_allow_html=True)
tb2.selectbox("Snapshot", ["Oct 2026  (snapshot)"], disabled=True,
              label_visibility="collapsed", key="snap")
if tb3.button("Share", use_container_width=True, type="secondary"):
    try:
        st.toast("Demo build - repo: bank-churn-bi", icon="i")
    except AttributeError:
        pass

st.write("")

# ---------- headline ----------
st.markdown('<div class="headline">Customer Churn: Who Do We Call '
            'First?</div>', unsafe_allow_html=True)
st.markdown('<div class="subline">10,000 retail bank customers (Kaggle) · '
            'snapshot Oct 2026</div>', unsafe_allow_html=True)
st.write("")

# ---------- KPI row ----------
k1, k2, k3, k4 = st.columns(4, gap="small")


def kpi_col(container, label, value, icon, note=""):
    with container:
        note_html = (f'<div class="kpi-note">{note}</div>' if note else "")
        st.markdown(
            f'<div class="kpi"><div class="kpi-flex">'
            f'<span class="kpi-ic">{icon}</span><div>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>{note_html}'
            f'</div></div></div>', unsafe_allow_html=True)


kpi_col(k1, "Total customers", fmt_int(snap["total"]), "👥")
kpi_col(k2, "Churned", fmt_int(CHURNED), "👤", "20.4% churn rate")
kpi_col(k3, "Churn rate", "20.4%", "%")
kpi_col(k4, "Save list", fmt_int(SAVE_N), "≡", f"{RISK8} scored 8+ risk")
st.write("")

# ---------- verdict callout ----------
st.markdown(
    f'<div class="callout"><div class="callout-title">CALL THESE '
    f'{fmt_int(SAVE_N)} DORMANT CUSTOMERS FIRST: {RISK8} SCORED 8+ '
    f'RISK.</div><div class="callout-sub">Top reason: {reason_en} '
    f'({TOP_N} of {SAVE_N}).</div></div>', unsafe_allow_html=True)
st.write("")

# ---------- row: map + donut ----------
m1, m2 = st.columns([.54, .46], gap="small")
with m1:
    tile_open("Churn rate by country", "3 countries in dataset")
    c_map, c_leg = st.columns([.62, .38], gap="small")
    c_map.plotly_chart(map_chart(), width="stretch",
                       config={"displayModeBar": False})
    with c_leg:
        shades = [RAMP[0], RAMP[2], RAMP[2]]
        for (g, r), col in zip(geo_rate.items(),
                               [RAMP[0], RAMP[3], RAMP[3]]):
            st.markdown(
                f'<div class="mrow"><span><span class="dot" '
                f'style="background:{col}"></span>{g}</span>'
                f'<span class="n">{fmt_pct(r)}</span></div>',
                unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="pill">Germany churns about 2x the rate of '
                    'France and Spain.</div>', unsafe_allow_html=True)
    st.caption("")

with m2:
    tile_open("Churned customers by product")
    d1, d2 = st.columns([.52, .48], gap="small")
    d1.plotly_chart(donut_chart(), width="stretch",
                    config={"displayModeBar": False})
    with d2:
        n_total = int(prod_counts.sum())
        for (n_prod, n_cust), col in zip(prod_counts.items(),
                                         [RAMP[0], RAMP[1], RAMP[2], RAMP[4]]):
            share = n_cust / n_total
            st.markdown(
                f'<div class="mrow"><span><span class="dot" '
                f'style="background:{col}"></span>'
                f'{n_prod} product{"s" if n_prod > 1 else ""}</span>'
                f'<span class="n">{fmt_int(n_cust)} '
                f'({fmt_pct(share, 0)})</span></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="pill">69% held only one product.</div>',
                    unsafe_allow_html=True)
    st.caption("")
st.write("")

# ---------- row: inactive vs active + tenure line ----------
g1, g2 = st.columns(2, gap="small")
with g1:
    tile_open("Churn rate: inactive vs active")
    st.plotly_chart(col_chart(), width="stretch",
                    config={"displayModeBar": False})
    st.caption("")
with g2:
    tile_open("Churn rate by tenure bucket", "Tenure barely moves the needle")
    st.plotly_chart(tenure_chart(), width="stretch",
                    config={"displayModeBar": False})
    st.caption("")
st.write("")

# ---------- row: worklist + reasons ----------
w1, w2 = st.columns([.55, .45], gap="small")
with w1:
    tile_open("Call worklist", "top 50 of 500, sort by risk score")
    rows = save.sort_values(["risk", "CustomerId"],
                            ascending=[False, True]).head(50)
    body = ""
    for _, r in rows.iterrows():
        a = .10 + .30 * (r["risk"] - 7) / 3
        chip = (f'<span class="chip" style="background:rgba(47,107,240,'
                f'{a:.2f})">{int(r["risk"])}</span>')
        body += (f"<tr><td>{r['CustomerId']}</td><td>{r['Geography']}</td>"
                 f"<td>{int(r['NumOfProducts'])}</td>"
                 f"<td>{int(r['Tenure'])}y</td><td>{chip}</td></tr>")
    st.markdown(
        f'<div class="worklist"><table><thead><tr><th>Customer ID</th>'
        f'<th>Country</th><th>Products</th><th>Tenure</th>'
        f'<th>Risk score</th></tr></thead><tbody>{body}</tbody></table>'
        f'</div>', unsafe_allow_html=True)

with w2:
    tile_open("Top 5 churn reasons",
              f"{fmt_pct(TOP_N / SAVE_N, 0)} = {reason_en}")
    st.plotly_chart(reasons_chart(), width="stretch",
                    config={"displayModeBar": False})
    st.caption("")

st.write("")
st.markdown('<div class="footer">Source: Kaggle Churn Modelling (10,000 '
            'rows) · marts via build_marts.py · snapshot Oct 2026</div>',
            unsafe_allow_html=True)
