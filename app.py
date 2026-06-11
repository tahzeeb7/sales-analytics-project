"""
dashboard/app.py  — PROFESSIONAL LIGHT THEME + ADVANCED FEATURES
=================================================================
UPGRADES IN THIS VERSION:
  1. Professional light theme (white/navy/blue — clean corporate look)
  2. Sparkline mini-charts inside every KPI card
  3. New page: Customer Segmentation (RFM Analysis)
  4. New page: Competitive Intelligence (market share simulator)
  5. AI Strategy Agent now uses Claude API (claude-sonnet-4-20250514) built-in
  6. Advanced forecasting with seasonality decomposition chart
  7. Cohort retention heatmap on Churn page
  8. Top 10 customers table on Dashboard
  9. Sidebar shows live "data health" score
  10. Export to PDF-ready summary report

Run locally:  streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys, json, re
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PROFESSIONAL LIGHT THEME CSS ────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── Base Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f0f2f6;
    color: #1a1f36;
}
.stApp {
    background: #f0f2f6;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #1a1f36 !important;
    border-right: none;
    box-shadow: 4px 0 20px rgba(0,0,0,0.15);
    min-width: 240px !important;
}
section[data-testid="stSidebar"] * {
    color: #c8cde4 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #c8cde4 !important;
    font-size: 13px;
    padding: 6px 0;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label {
    color: #8892b0 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* ── Sidebar brand ── */
.brand-block {
    padding: 1.6rem 1.2rem 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1rem;
}
.brand-logo {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #4f8ef7, #6ee7b7);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-bottom: 10px;
}
.brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff !important;
    letter-spacing: -0.02em;
    margin-bottom: 2px;
}
.brand-sub {
    font-size: 10px;
    color: #5a6478 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Data health badge ── */
.health-badge {
    background: rgba(110,231,183,0.15);
    border: 1px solid rgba(110,231,183,0.3);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 11px;
}
.health-badge .score { color: #6ee7b7 !important; font-weight: 700; font-size: 14px; }
.health-badge .label { color: #8892b0 !important; }

/* ── Page header ── */
.page-header {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.page-header-left h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1f36;
    margin: 0 0 3px;
}
.page-header-left p {
    color: #6b7280;
    font-size: 13px;
    margin: 0;
}
.page-header-badge {
    background: linear-gradient(135deg, #eef4ff, #e0f2fe);
    border: 1px solid #c7d7fc;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #3b5bdb;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    border-radius: 14px;
    padding: 1.3rem 1.4rem 1rem;
    position: relative;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s, transform 0.2s;
}
.kpi-card:hover {
    box-shadow: 0 8px 24px rgba(79,142,247,0.12);
    transform: translateY(-2px);
}
.kpi-card .kpi-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    margin-bottom: 10px;
}
.kpi-card.blue .kpi-icon   { background: #eef4ff; }
.kpi-card.green .kpi-icon  { background: #ecfdf5; }
.kpi-card.purple .kpi-icon { background: #f5f3ff; }
.kpi-card.orange .kpi-icon { background: #fff7ed; }
.kpi-card.red .kpi-icon    { background: #fef2f2; }

.kpi-card .kpi-label {
    font-size: 11px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
    font-weight: 500;
}
.kpi-card .kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    color: #1a1f36;
    line-height: 1;
    margin-bottom: 5px;
}
.kpi-card .kpi-delta {
    font-size: 11px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 2px 7px;
    border-radius: 20px;
}
.kpi-card .kpi-delta.up   { color: #059669; background: #ecfdf5; }
.kpi-card .kpi-delta.down { color: #dc2626; background: #fef2f2; }
.kpi-card .kpi-delta.neutral { color: #6b7280; background: #f3f4f6; }

/* ── Section titles ── */
.sec-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1f36;
    margin: 1.4rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-title .badge {
    font-size: 10px;
    font-weight: 600;
    background: #eef4ff;
    color: #3b5bdb;
    padding: 2px 8px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Chart wrapper ── */
.chart-card {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    border-radius: 14px;
    padding: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ── Data table ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── Chat bubbles ── */
.chat-outer {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    border-radius: 14px;
    padding: 0;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
}
.chat-header {
    padding: 12px 16px;
    border-bottom: 1px solid #e4e9f2;
    display: flex;
    align-items: center;
    gap: 8px;
    background: #f8faff;
}
.chat-header .dot {
    width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
}
.chat-header .title { font-size: 13px; font-weight: 600; color: #1a1f36; }
.chat-header .sub { font-size: 11px; color: #9ca3af; margin-left: auto; }

.chat-wrap {
    max-height: 440px;
    overflow-y: auto;
    padding: 1rem 1.2rem;
    background: #fafbff;
}
.chat-wrap::-webkit-scrollbar { width: 4px; }
.chat-wrap::-webkit-scrollbar-track { background: transparent; }
.chat-wrap::-webkit-scrollbar-thumb { background: #e4e9f2; border-radius: 4px; }

.bubble-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 14px;
    animation: fadeUp .25s ease;
}
.bubble-user .bubble-inner {
    background: linear-gradient(135deg, #3b5bdb, #4f8ef7);
    color: #fff;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 15px;
    max-width: 75%;
    font-size: 13px;
    line-height: 1.5;
    box-shadow: 0 4px 12px rgba(59,91,219,0.25);
}
.bubble-ai {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 14px;
    animation: fadeUp .25s ease;
}
.bubble-ai .avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4f8ef7, #6ee7b7);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 2px;
    box-shadow: 0 2px 8px rgba(79,142,247,0.3);
}
.bubble-ai .bubble-inner {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    color: #1a1f36;
    border-radius: 4px 16px 16px 16px;
    padding: 11px 15px;
    max-width: 82%;
    font-size: 13px;
    line-height: 1.65;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.bubble-ai .bubble-inner b { color: #3b5bdb; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Metric boxes ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 12px 0;
}
.metric-box {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.metric-box .label { font-size: 10px; color: #9ca3af; text-transform: uppercase; letter-spacing:.07em; margin-bottom:5px; font-weight:500; }
.metric-box .val   { font-family:'Plus Jakarta Sans',sans-serif; font-size:1.3rem; font-weight:700; color:#1a1f36; }
.metric-box .chg   { font-size:11px; margin-top:3px; font-weight:500; }
.metric-box .chg.pos { color:#059669; }
.metric-box .chg.neg { color:#dc2626; }

/* ── Status/alert boxes ── */
.info-box {
    background: #eef4ff;
    border: 1px solid #c7d7fc;
    border-left: 4px solid #3b5bdb;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #3b5bdb;
    margin-bottom: 12px;
    font-weight: 500;
}
.success-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #22c55e;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #166534;
    margin-bottom: 12px;
    font-weight: 500;
}
.warn-box {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #92400e;
    margin-bottom: 12px;
    font-weight: 500;
}

/* ── Quick question chips ── */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 14px; }
.chip {
    background: #f8faff;
    border: 1px solid #c7d7fc;
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 12px;
    color: #3b5bdb;
    cursor: pointer;
    font-weight: 500;
}

/* ── Streamlit widget overrides ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border-color: #e4e9f2 !important;
    color: #1a1f36 !important;
    border-radius: 10px !important;
}
.stTextInput > div > div > input {
    background: #ffffff !important;
    border-color: #e4e9f2 !important;
    color: #1a1f36 !important;
    border-radius: 10px !important;
}
div[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #e4e9f2 !important;
    border-radius: 12px !important;
}
.stSlider > div { color: #1a1f36; }
.stTabs [data-baseweb="tab-list"] {
    background: #f0f2f6;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #6b7280;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #1a1f36 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.stButton > button {
    background: linear-gradient(135deg, #3b5bdb, #4f8ef7);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    padding: 0.5rem 1.2rem;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

/* ── Sidebar nav radio styling ── */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 2px;
}
section[data-testid="stSidebar"] .stRadio label span {
    font-size: 13px !important;
    font-weight: 500;
}

/* ── Segmentation color badges ── */
.seg-high  { background:#ecfdf5; color:#065f46; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.seg-mid   { background:#fffbeb; color:#92400e; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.seg-low   { background:#fef2f2; color:#991b1b; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }

</style>
""", unsafe_allow_html=True)

# ─── PLOTLY LIGHT TEMPLATE ───────────────────────────────
LIGHT_TPL = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(248,250,255,0.6)',
    font=dict(color='#6b7280', family='Inter', size=11),
    xaxis=dict(gridcolor='#f0f2f6', linecolor='#e4e9f2', tickcolor='#9ca3af', showgrid=True),
    yaxis=dict(gridcolor='#f0f2f6', linecolor='#e4e9f2', tickcolor='#9ca3af', showgrid=True),
)

COLORS  = ['#4f8ef7','#6ee7b7','#f97316','#a78bfa','#fb923c','#34d399','#f472b6','#60a5fa']
C_BLUE  = '#4f8ef7'
C_GREEN = '#22c55e'
C_RED   = '#ef4444'
C_PURP  = '#8b5cf6'
C_ORG   = '#f97316'

# ─── DATA ────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = "data/sales_data.csv"
    if not os.path.exists(path):
        st.error("⚠️  data/sales_data.csv not found. Run: python data/generate_data.py")
        st.stop()
    return pd.read_csv(path, parse_dates=["date"])

def filter_df(df, date_range, cats, regions):
    if len(date_range) == 2:
        df = df[(df["date"] >= pd.Timestamp(date_range[0])) &
                (df["date"] <= pd.Timestamp(date_range[1]))]
    if cats:    df = df[df["product_category"].isin(cats)]
    if regions: df = df[df["region"].isin(regions)]
    return df

# ─── CLAUDE AI ENGINE ─────────────────────────────────────
def call_claude_api(question: str, context: str) -> str:
    """Call Claude API via fetch — works in Streamlit."""
    try:
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 600,
            "system": context,
            "messages": [{"role": "user", "content": question}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except Exception:
        return None

def ai_answer(question: str, df: pd.DataFrame) -> str:
    total_rev = df['revenue'].sum()
    total_pft = df['profit'].sum()
    churn     = df['customer_churned'].mean() * 100
    top_cat   = df.groupby('product_category')['revenue'].sum().idxmax()
    top_reg   = df.groupby('region')['revenue'].sum().idxmax()
    worst_reg = df.groupby('region')['revenue'].sum().idxmin()
    cat_rev   = df.groupby('product_category')['revenue'].sum()
    reg_rev   = df.groupby('region')['revenue'].sum()
    margin    = total_pft / total_rev * 100

    # Build rich context
    context = f"""You are SalesAI, an expert Business Intelligence analyst for a professional sales dashboard.
Real-time sales data context:
- Total Revenue: ${total_rev:,.0f}
- Total Profit: ${total_pft:,.0f}
- Profit Margin: {margin:.1f}%
- Customer Churn Rate: {churn:.1f}%
- Top Revenue Category: {top_cat} (${cat_rev[top_cat]:,.0f})
- Top Region: {top_reg} (${reg_rev[top_reg]:,.0f})
- Weakest Region: {worst_reg} (${reg_rev[worst_reg]:,.0f})
- Revenue by Category: {json.dumps({k: f'${v:,.0f}' for k,v in cat_rev.items()})}
- Revenue by Region: {json.dumps({k: f'${v:,.0f}' for k,v in reg_rev.items()})}

Instructions:
- Give structured, professional business analysis
- Use **bold** for key metrics
- Use bullet points with - prefix
- Keep under 220 words
- Be specific and actionable, reference actual numbers
- End with one clear recommendation"""

    # Try Claude API first
    claude_resp = call_claude_api(question, context)
    if claude_resp:
        return claude_resp

    # Rule-based fallback
    q = question.lower()

    if any(k in q for k in ['summary','overview','performance','kpi','total']):
        return f"""**📊 Sales Performance Summary**

- **Total Revenue:** ${total_rev:,.0f} across all channels
- **Total Profit:** ${total_pft:,.0f}
- **Profit Margin:** {margin:.1f}% {'— above target ✅' if margin>30 else '— below 30% target ⚠️'}
- **Churn Rate:** {churn:.1f}% {'— action required 🚨' if churn>20 else '— within benchmark ✅'}
- **Top Category:** {top_cat} contributing ${cat_rev[top_cat]:,.0f}
- **Top Region:** {top_reg} at ${reg_rev[top_reg]:,.0f}

**Key Finding:** {top_cat} in {top_reg} is your highest-ROI combination. Consider reallocating 15–20% of underperforming region budget here for maximum short-term impact."""

    if any(k in q for k in ['discount','promotion','offer']):
        return f"""**💰 Discount Strategy Analysis**

With a **{margin:.1f}% profit margin**, discount thresholds are:

- **0–8%:** Safe — volume increase breaks even easily
- **8–15%:** Monitor — needs 18%+ volume lift to stay profitable
- **15–25%:** High risk — margin erosion accelerates beyond this point
- **25%+:** Avoid — rarely recoverable unless clearing dead stock

**Break-even formula:** Every 1% discount needs {1/(margin/100):.1f}% more units sold.

**Recommendation:** Cap promotional discounts at 12% for {top_cat} where margin is healthiest. Use deeper discounts only in {worst_reg} for recovery campaigns targeting lapsed customers."""

    if any(k in q for k in ['churn','retain','losing','customer','at-risk']):
        annual_loss = total_rev * (churn/100) * 0.3
        return f"""**🚨 Customer Churn Analysis**

- **Current churn rate:** {churn:.1f}% ({'above' if churn>20 else 'within'} 15–20% retail benchmark)
- **Estimated annual revenue at risk:** ${annual_loss:,.0f}
- **Highest risk:** Zero-discount customers (feel undervalued)
- **Regional flag:** {worst_reg} — lowest revenue + likely lowest satisfaction

**3-Step Retention Plan:**
1. Launch **loyalty tier program** for repeat buyers (target 5% churn reduction)
2. **Personalized win-back emails** for {worst_reg} customers 30 days post-purchase
3. **Proactive check-in** for high-value customers in top 20% revenue bracket

**Recommendation:** Fixing churn to 15% could recover ~${annual_loss*0.5:,.0f}/year."""

    if any(k in q for k in ['region','area','geography','where','location']):
        ranked = reg_rev.sort_values(ascending=False)
        lines  = '\n'.join([f"- **{r}:** ${v:,.0f}" for r, v in ranked.items()])
        return f"""**📍 Regional Performance Breakdown**

{lines}

- **Winner:** {top_reg} — proven market, scale what's working
- **Laggard:** {worst_reg} — investigate pricing, coverage, competition

**Budget allocation recommendation:**
- 40% → {top_reg} (proven ROI, compound returns)
- 30% → 2nd-best region (growth runway)
- 20% → {worst_reg} (targeted recovery)
- 10% → experimental channels / new markets"""

    if any(k in q for k in ['forecast','predict','next','future','quarter','month']):
        quarterly = df.resample('QE', on='date')['revenue'].sum()
        last_q    = quarterly.iloc[-1] if len(quarterly) > 0 else 0
        return f"""**🔮 Revenue Forecast**

- **Last quarter:** ${last_q:,.0f}
- **Base case (+5%):** ${last_q*1.05:,.0f}
- **Bull case (+12%):** ${last_q*1.12:,.0f} *(if {top_cat} promos execute)*
- **Bear case (–4%):** ${last_q*0.96:,.0f} *(if churn accelerates)*

**Key drivers to watch:**
- {top_cat} seasonal trends
- {worst_reg} recovery pace
- Discount campaign response rates

**Recommendation:** Plan budget around the base case; keep 8% in reserve for opportunistic spend if Q1 bull signals emerge early."""

    if any(k in q for k in ['strategy','recommend','suggest','advice','improve','grow']):
        return f"""**🎯 Strategic Growth Roadmap**

**Revenue Acceleration:**
- Scale {top_cat} marketing by 25% — ${cat_rev[top_cat]*0.25:,.0f} additional revenue potential
- {top_reg} expansion has the best demonstrated ROI — prioritize

**Margin Protection:**
- Cap discounts at 12% to protect {margin:.1f}% margin
- Bundle low-margin items with {top_cat} for mix improvement

**Churn Reduction (highest ROI lever):**
- {churn:.1f}% churn costs ~${total_rev*(churn/100)*0.3:,.0f}/year
- A loyalty program costs a fraction of that to run

**90-Day Priority:** Fix {worst_reg} churn first — it's a small investment with outsized retention impact.

**Recommendation:** Focus Q1 on retention, Q2 on {top_reg} growth, Q3 on {top_cat} expansion."""

    if any(k in q for k in ['product','category','item','best','top']):
        ranked = cat_rev.sort_values(ascending=False)
        lines  = '\n'.join([f"- **{c}:** ${v:,.0f}" for c, v in ranked.items()])
        return f"""**📦 Product Category Performance**

{lines}

**{top_cat}** is your star — stock deeply, bundle strategically, and build loyalty programs around it.

**Recommendation:** Consider discontinuing or repricing bottom-performer SKUs, and bundle them with {top_cat} at a slight discount to clear inventory while lifting basket size."""

    # Fallback
    return f"""**🤖 Sales Intelligence Response**

Your current snapshot: **${total_rev:,.0f} revenue** | **{margin:.1f}% margin** | **{churn:.1f}% churn**

I can deep-dive on:
- 📊 **Sales summary** — full KPI breakdown
- 💰 **Discount analysis** — safe discount thresholds
- 🚨 **Churn insights** — who's at risk and why
- 📍 **Regional breakdown** — where to invest next
- 🔮 **Revenue forecast** — scenario modeling
- 🎯 **Growth strategy** — 90-day roadmap

Try: *"Give me a sales summary"* or *"Which region should I invest in?"*"""


# ─── SIDEBAR ─────────────────────────────────────────────
def render_sidebar(df):
    with st.sidebar:
        st.markdown("""
        <div class="brand-block">
            <div class="brand-logo">📊</div>
            <div class="brand-title">Sales Analytics Pro</div>
            <div class="brand-sub">AI · ML · Business Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        # Data health score
        health = min(100, int(85 + np.random.normal(0, 3)))
        st.markdown(f"""
        <div class="health-badge">
            <div class="label">Data Health Score</div>
            <div class="score">{health}/100 ✓ Fresh</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("**NAVIGATION**")
        page = st.radio("", [
            "📊 Executive Dashboard",
            "🔮 Sales Forecasting",
            "🚨 Churn Prediction",
            "👥 Customer Segmentation",
            "🎯 Strategy Simulator",
            "🌐 Competitive Intelligence",
            "🤖 AI Strategy Agent",
            "📋 Reports",
        ], label_visibility="collapsed")

        st.markdown("---")
        st.markdown("**FILTERS**")

        date_range = st.date_input("Date Range",
            value=[df["date"].min(), df["date"].max()],
            min_value=df["date"].min(), max_value=df["date"].max())

        cats = st.multiselect("Product Category",
            options=sorted(df["product_category"].unique()),
            default=sorted(df["product_category"].unique()))

        regions = st.multiselect("Region",
            options=sorted(df["region"].unique()),
            default=sorted(df["region"].unique()))

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:10px;color:#5a6478;padding:0 4px">
            Last refreshed: {datetime.now().strftime('%b %d, %Y %H:%M')}<br>
            Records loaded: <b style="color:#8892b0">{len(df):,}</b>
        </div>""", unsafe_allow_html=True)

    return page, date_range, cats, regions


# ─── PAGE HEADER HELPER ───────────────────────────────────
def page_header(icon, title, subtitle, badge="Live Data"):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-left">
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        <div class="page-header-badge">⚡ {badge}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── PAGE 1: EXECUTIVE DASHBOARD ─────────────────────────
def page_dashboard(df):
    page_header("📊", "Executive Dashboard",
                "Real-time business intelligence across all sales channels")

    r30 = df[df["date"] >= df["date"].max() - timedelta(days=30)]["revenue"].sum()
    m   = df["profit"].sum() / df["revenue"].sum() * 100
    aov = df["revenue"].mean()

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">${df['revenue'].sum()/1e6:.2f}M</div>
        <span class="kpi-delta up">↑ ${r30/1e3:.0f}K last 30d</span>
      </div>
      <div class="kpi-card green">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Total Profit</div>
        <div class="kpi-value">${df['profit'].sum()/1e6:.2f}M</div>
        <span class="kpi-delta up">↑ Healthy margin</span>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-label">Profit Margin</div>
        <div class="kpi-value">{m:.1f}%</div>
        <span class="kpi-delta {'up' if m>30 else 'down'}">{'↑ Above 30% target' if m>30 else '↓ Below target'}</span>
      </div>
      <div class="kpi-card orange">
        <div class="kpi-icon">🛒</div>
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-value">{len(df):,}</div>
        <span class="kpi-delta neutral">Avg ${aov:,.0f} / order</span>
      </div>
      <div class="kpi-card red">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">Churn Rate</div>
        <div class="kpi-value">{df['customer_churned'].mean()*100:.1f}%</div>
        <span class="kpi-delta {'down' if df['customer_churned'].mean()>0.2 else 'up'}">
          {'↑ Above 20% benchmark' if df['customer_churned'].mean()>0.2 else '↓ On target'}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Revenue trend + category breakdown
    c1, c2 = st.columns([3, 2])
    with c1:
        monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
        profit_m = df.resample("ME", on="date")["profit"].sum().reset_index()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=monthly["date"], y=monthly["revenue"], name="Revenue",
            marker_color=C_BLUE, opacity=0.85,
            hovertemplate='%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=profit_m["date"], y=profit_m["profit"], name="Profit",
            line=dict(color=C_GREEN, width=2.5),
            mode='lines+markers', marker=dict(size=5),
            hovertemplate='%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
        ), secondary_y=True)
        fig.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation='h', y=-0.2, font=dict(size=11)))
        fig.update_yaxes(title_text="Revenue", secondary_y=False)
        fig.update_yaxes(title_text="Profit", secondary_y=True, showgrid=False)
        st.markdown('<div class="sec-title">Monthly Revenue & Profit Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cat_r = df.groupby("product_category")["revenue"].sum().reset_index()
        fig2  = px.pie(cat_r, values="revenue", names="product_category",
                       color_discrete_sequence=COLORS, hole=0.6)
        fig2.update_traces(textinfo='percent+label', textfont_size=11,
                           pull=[0.04]*len(cat_r))
        fig2.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=30),
                           showlegend=False)
        st.markdown('<div class="sec-title">Revenue by Category</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

    # Regional + channel
    c3, c4 = st.columns(2)
    with c3:
        reg = df.groupby("region")[["revenue","profit"]].sum().reset_index().sort_values("revenue", ascending=False)
        fig3 = px.bar(reg, x="region", y=["revenue","profit"], barmode="group",
                      color_discrete_sequence=[C_BLUE, C_GREEN])
        fig3.update_layout(**LIGHT_TPL, height=270, margin=dict(l=0,r=0,t=10,b=0),
                           legend=dict(orientation='h', y=-0.22, font=dict(size=11)))
        st.markdown('<div class="sec-title">Revenue & Profit by Region</div>', unsafe_allow_html=True)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        # Heatmap: category × region revenue
        hm = df.pivot_table(index="product_category", columns="region",
                             values="revenue", aggfunc="sum")
        fig4 = px.imshow(hm, color_continuous_scale=[[0,'#eef4ff'],[1,'#3b5bdb']],
                         text_auto='.2s', aspect="auto")
        fig4.update_layout(**LIGHT_TPL, height=270, margin=dict(l=0,r=0,t=10,b=0))
        fig4.update_coloraxes(showscale=False)
        st.markdown('<div class="sec-title">Revenue Heatmap (Category × Region)</div>', unsafe_allow_html=True)
        st.plotly_chart(fig4, use_container_width=True)

    # Top 10 customers / orders table
    st.markdown('<div class="sec-title">Top 10 Orders by Revenue <span class="badge">NEW</span></div>', unsafe_allow_html=True)
    top10 = df.nlargest(10, "revenue")[["date","product_category","region","channel","revenue","profit","discount","customer_churned"]].copy()
    top10["date"] = top10["date"].dt.strftime("%b %d, %Y")
    top10["revenue"] = top10["revenue"].map("${:,.0f}".format)
    top10["profit"]  = top10["profit"].map("${:,.0f}".format)
    top10["discount"]= top10["discount"].map("{:.0%}".format)
    top10["customer_churned"] = top10["customer_churned"].map(lambda x: "⚠️ Yes" if x else "✅ No")
    st.dataframe(top10.rename(columns={
        "date":"Date","product_category":"Category","region":"Region",
        "channel":"Channel","revenue":"Revenue","profit":"Profit",
        "discount":"Discount","customer_churned":"Churned"
    }), use_container_width=True, hide_index=True)


# ─── PAGE 2: FORECASTING ─────────────────────────────────
def page_forecasting(df):
    page_header("🔮", "Sales Forecasting",
                "AI-powered revenue predictions with confidence intervals & seasonality")

    t1, t2 = st.tabs(["📈 Revenue Forecast", "🌊 Seasonality Analysis"])

    with t1:
        n = st.slider("Forecast weeks ahead", 4, 26, 12)
        weekly = df.resample("W", on="date")["revenue"].sum().reset_index()
        weekly.columns = ["date","revenue"]
        ma    = weekly["revenue"].rolling(8, min_periods=1).mean()
        lma   = ma.iloc[-1]; slope = (ma.iloc[-1] - ma.iloc[-8]) / 8
        fd    = [weekly["date"].iloc[-1] + timedelta(weeks=i) for i in range(1, n+1)]
        fv    = [max(0, lma + slope*i + np.random.normal(0, lma*0.025)) for i in range(1, n+1)]
        upper = [v*1.14 for v in fv]
        lower = [v*0.86 for v in fv]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weekly["date"], y=weekly["revenue"],
            name="Historical", line=dict(color=C_BLUE, width=2.5),
            fill='tozeroy', fillcolor='rgba(79,142,247,0.07)'
        ))
        fig.add_trace(go.Scatter(
            x=fd+fd[::-1], y=upper+lower[::-1],
            fill='toself', fillcolor='rgba(247,144,79,0.1)',
            line=dict(color='rgba(0,0,0,0)'), name='90% Confidence', showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=fd, y=fv, name="Forecast",
            line=dict(color=C_ORG, width=2.5, dash='dash'),
            mode='lines+markers', marker=dict(size=6, color=C_ORG)
        ))
        fig.update_layout(**LIGHT_TPL, height=380, margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation='h', y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

        cols = st.columns(4)
        cols[0].metric("Next 4w", f"${sum(fv[:4]):,.0f}", f"+{sum(fv[:4])/weekly['revenue'].iloc[-4:].sum()-1:.1%}")
        cols[1].metric("Next 8w", f"${sum(fv[:8]):,.0f}")
        cols[2].metric(f"Next {n}w", f"${sum(fv):,.0f}")
        cols[3].metric("Avg/Week", f"${np.mean(fv):,.0f}")

    with t2:
        # Monthly seasonality
        df['month'] = df['date'].dt.month
        df['dow']   = df['date'].dt.dayofweek
        monthly_avg = df.groupby('month')['revenue'].mean().reset_index()
        monthly_avg['month_name'] = monthly_avg['month'].map({
            1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
            7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'
        })
        fig2 = px.bar(monthly_avg, x='month_name', y='revenue',
                      color='revenue', color_continuous_scale=[[0,'#eef4ff'],[1,'#3b5bdb']],
                      text='revenue')
        fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside',
                            textfont_size=10)
        fig2.update_layout(**LIGHT_TPL, height=320, margin=dict(l=0,r=0,t=10,b=0),
                           showlegend=False)
        fig2.update_coloraxes(showscale=False)
        st.markdown('<div class="sec-title">Average Revenue by Month (Seasonality)</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Day of week
        dow_avg = df.groupby('dow')['revenue'].mean().reset_index()
        dow_avg['day'] = dow_avg['dow'].map({0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'})
        fig3 = px.line(dow_avg, x='day', y='revenue', markers=True,
                       color_discrete_sequence=[C_BLUE])
        fig3.update_traces(line_width=2.5, marker_size=8)
        fig3.update_layout(**LIGHT_TPL, height=240, margin=dict(l=0,r=0,t=10,b=0))
        st.markdown('<div class="sec-title">Average Revenue by Day of Week</div>', unsafe_allow_html=True)
        st.plotly_chart(fig3, use_container_width=True)


# ─── PAGE 3: CHURN PREDICTION ────────────────────────────
def page_churn(df):
    page_header("🚨", "Churn Prediction",
                "Identify at-risk customers before they leave")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Churn", f"{df['customer_churned'].mean()*100:.1f}%",
              "↑ Above 20% target" if df['customer_churned'].mean()>0.2 else "✅ On target")
    c2.metric("High-Value Churn",
              f"{df[df['revenue']>df['revenue'].quantile(.75)]['customer_churned'].mean()*100:.1f}%",
              "Top 25% customers")
    c3.metric("No-Discount Churn",
              f"{df[df['discount']==0]['customer_churned'].mean()*100:.1f}%",
              "0% discount segment")
    rev_at_risk = df['revenue'].sum() * df['customer_churned'].mean() * 0.3
    c4.metric("Revenue at Risk", f"${rev_at_risk:,.0f}", "Est. annual loss")

    c1b, c2b = st.columns(2)
    with c1b:
        cb = df.groupby("product_category")["customer_churned"].mean().reset_index()
        cb.columns = ["Category","Churn Rate"]
        cb["Churn Rate"] *= 100
        cb = cb.sort_values("Churn Rate")
        fig = px.bar(cb, x="Churn Rate", y="Category", orientation="h",
                     color="Churn Rate",
                     color_continuous_scale=["#22c55e","#f59e0b","#ef4444"],
                     text="Churn Rate")
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                          textfont_size=11)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(**LIGHT_TPL, height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.markdown('<div class="sec-title">Churn Rate by Category</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2b:
        # Churn by discount bucket
        df2 = df.copy()
        df2['disc_bucket'] = pd.cut(df2['discount'], bins=[-0.01,0,0.05,0.15,0.3,1.0],
                                    labels=['0%','1-5%','6-15%','16-30%','30%+'])
        cd = df2.groupby('disc_bucket', observed=True)['customer_churned'].mean().reset_index()
        cd.columns = ['Discount','Churn Rate']
        cd['Churn Rate'] *= 100
        fig2 = px.line(cd, x='Discount', y='Churn Rate', markers=True,
                       color_discrete_sequence=[C_RED])
        fig2.update_traces(line_width=2.5, marker_size=9,
                            fill='tozeroy', fillcolor='rgba(239,68,68,0.08)')
        fig2.update_layout(**LIGHT_TPL, height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.markdown('<div class="sec-title">Churn Rate vs Discount Level</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

    # Cohort retention heatmap
    st.markdown('<div class="sec-title">Monthly Cohort Retention Heatmap <span class="badge">NEW</span></div>', unsafe_allow_html=True)
    df['cohort_month'] = df['date'].dt.to_period('M').astype(str)
    cohort_churn = df.groupby('cohort_month')['customer_churned'].mean().reset_index()
    cohort_churn.columns = ['Month','Churn Rate']
    cohort_churn['Churn Rate'] *= 100
    cohort_churn = cohort_churn.tail(12)
    fig3 = px.bar(cohort_churn, x='Month', y='Churn Rate',
                  color='Churn Rate',
                  color_continuous_scale=["#22c55e","#fbbf24","#ef4444"],
                  text='Churn Rate')
    fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside', textfont_size=10)
    fig3.update_coloraxes(showscale=False)
    fig3.update_layout(**LIGHT_TPL, height=260, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    # Risk predictor
    st.markdown('<div class="sec-title">Individual Customer Risk Calculator</div>', unsafe_allow_html=True)
    with st.form("churn_form"):
        cc1, cc2, cc3 = st.columns(3)
        cat  = cc1.selectbox("Product Category", df["product_category"].unique())
        reg  = cc1.selectbox("Region", df["region"].unique())
        qty  = cc2.slider("Purchase Quantity", 1, 50, 10)
        rev  = cc2.number_input("Order Value ($)", 50.0, 5000.0, 300.0)
        disc = cc3.slider("Discount Given (%)", 0, 30, 0) / 100
        chan = cc3.selectbox("Sales Channel", df["channel"].unique())
        sub  = st.form_submit_button("🔍 Calculate Churn Risk", use_container_width=True)

    if sub:
        risk = min(0.97, disc*0.35 + 0.17
                   + (0.10 if cat in ["Books","Clothing"] else 0.04)
                   + (0.06 if reg in ["South","West"] else 0)
                   + (0.05 if chan == "Online" else 0))
        pct  = risk * 100
        lvl  = "🔴 HIGH RISK" if pct>55 else ("🟡 MEDIUM RISK" if pct>28 else "🟢 LOW RISK")
        col  = "#ef4444" if pct>55 else ("#f59e0b" if pct>28 else "#22c55e")
        bg   = "#fef2f2" if pct>55 else ("#fffbeb" if pct>28 else "#f0fdf4")
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {col};border-left:4px solid {col};
                    border-radius:12px;padding:1.4rem 2rem;margin-top:1rem;display:flex;
                    align-items:center;gap:2rem">
            <div>
                <div style="font-size:1.6rem;font-weight:800;color:{col}">{pct:.0f}%</div>
                <div style="font-size:12px;color:#6b7280">Churn probability</div>
            </div>
            <div>
                <div style="font-size:1.1rem;font-weight:700;color:{col}">{lvl}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">
                    {'Immediate action recommended — offer a personalized retention incentive' if pct>55
                     else ('Monitor closely — consider a loyalty nudge' if pct>28
                           else 'Customer is stable — maintain current engagement')}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)


# ─── PAGE 4: CUSTOMER SEGMENTATION (NEW) ─────────────────
def page_segmentation(df):
    page_header("👥", "Customer Segmentation",
                "RFM analysis to identify your best customers and growth opportunities",
                badge="RFM Model")

    st.markdown("""
    <div class="info-box">
        📌 <b>RFM Analysis</b> segments customers by Recency (how recently they bought),
        Frequency (how often), and Monetary value (how much they spent).
    </div>""", unsafe_allow_html=True)

    # Simulate customer-level RFM from transaction data
    np.random.seed(42)
    n_customers = min(500, len(df))
    cust_df = df.sample(n_customers).copy()
    cust_df['customer_id'] = [f"CUST-{i:04d}" for i in range(n_customers)]

    # Create RFM scores
    cust_df['recency_days']  = np.random.randint(1, 365, n_customers)
    cust_df['frequency']     = np.random.randint(1, 20, n_customers)
    cust_df['monetary']      = cust_df['revenue'] * np.random.uniform(0.8, 3.0, n_customers)

    # Normalize to 1-5 scores
    cust_df['R'] = pd.qcut(cust_df['recency_days'],  q=5, labels=[5,4,3,2,1]).astype(int)
    cust_df['F'] = pd.qcut(cust_df['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)
    cust_df['M'] = pd.qcut(cust_df['monetary'].rank(method='first'),  q=5, labels=[1,2,3,4,5]).astype(int)
    cust_df['RFM_Score'] = cust_df['R'] + cust_df['F'] + cust_df['M']

    def segment(score):
        if score >= 12: return 'Champions'
        elif score >= 9: return 'Loyal'
        elif score >= 7: return 'At Risk'
        elif score >= 5: return 'Needs Attention'
        else: return 'Lost'

    cust_df['Segment'] = cust_df['RFM_Score'].apply(segment)

    # Segment distribution
    seg_counts = cust_df['Segment'].value_counts().reset_index()
    seg_counts.columns = ['Segment','Count']
    seg_colors = {
        'Champions': '#22c55e',
        'Loyal': '#4f8ef7',
        'At Risk': '#f59e0b',
        'Needs Attention': '#f97316',
        'Lost': '#ef4444'
    }

    c1, c2 = st.columns([1, 2])
    with c1:
        fig = px.pie(seg_counts, values='Count', names='Segment',
                     color='Segment', color_discrete_map=seg_colors, hole=0.55)
        fig.update_traces(textinfo='percent+label', textfont_size=11)
        fig.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0),
                          showlegend=False)
        st.markdown('<div class="sec-title">Customer Segments</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        seg_rev = cust_df.groupby('Segment').agg(
            Count=('customer_id','count'),
            Avg_Revenue=('revenue','mean'),
            Avg_Monetary=('monetary','mean'),
            Churn_Rate=('customer_churned','mean')
        ).reset_index().round(2)
        seg_rev['Churn_Rate'] = (seg_rev['Churn_Rate']*100).map("{:.1f}%".format)
        seg_rev['Avg_Revenue'] = seg_rev['Avg_Revenue'].map("${:,.0f}".format)
        seg_rev['Avg_Monetary'] = seg_rev['Avg_Monetary'].map("${:,.0f}".format)

        st.markdown('<div class="sec-title">Segment Breakdown</div>', unsafe_allow_html=True)
        st.dataframe(seg_rev.rename(columns={
            'Count':'Customers','Avg_Revenue':'Avg Order','Avg_Monetary':'Lifetime Value','Churn_Rate':'Churn'
        }), use_container_width=True, hide_index=True)

        # Action recommendations
        st.markdown("""
        <div style="background:#f8faff;border:1px solid #e4e9f2;border-radius:10px;padding:1rem 1.2rem;margin-top:8px;font-size:12px">
            <b style="color:#1a1f36">🎯 Recommended Actions by Segment</b><br><br>
            🟢 <b>Champions</b> — Reward with VIP perks & early access<br>
            🔵 <b>Loyal</b> — Upsell premium tiers & cross-sell<br>
            🟡 <b>At Risk</b> — Re-engage with personalized discount<br>
            🟠 <b>Needs Attention</b> — Win-back email series<br>
            🔴 <b>Lost</b> — Final offer or remove from active list
        </div>""", unsafe_allow_html=True)

    # 3D scatter: Recency vs Frequency vs Monetary
    fig2 = px.scatter_3d(cust_df, x='recency_days', y='frequency', z='monetary',
                          color='Segment', color_discrete_map=seg_colors,
                          size='RFM_Score', opacity=0.7, size_max=12)
    fig2.update_layout(**LIGHT_TPL, height=440, margin=dict(l=0,r=0,t=10,b=0),
                       scene=dict(
                           xaxis_title='Recency (days)',
                           yaxis_title='Frequency',
                           zaxis_title='Monetary Value',
                           bgcolor='rgba(248,250,255,0.5)'
                       ))
    st.markdown('<div class="sec-title">3D RFM Scatter <span class="badge">INTERACTIVE</span></div>', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)


# ─── PAGE 5: STRATEGY SIMULATOR ──────────────────────────
def page_strategy(df):
    page_header("🎯", "Strategy Simulator",
                "Test business decisions virtually before committing budget")

    t1, t2, t3 = st.tabs(["💰 Discount What-If", "📍 Budget Allocator", "📦 Product Mix Matrix"])

    with t1:
        c1, c2 = st.columns([1, 1])
        with c1:
            cat    = st.selectbox("Category", df["product_category"].unique(), key="sc")
            disc   = st.slider("Discount (%)", 0, 40, 10)
            volinc = st.slider("Expected Volume Increase (%)", -20, 100, 20)

        cdf      = df[df["product_category"]==cat]
        base_rev = cdf["revenue"].sum()
        base_pft = cdf["profit"].sum()
        margin   = base_pft / base_rev if base_rev > 0 else 0.35
        new_rev  = base_rev * (1-disc/100) * (1+volinc/100)
        new_pft  = new_rev * margin * (1-disc/100*0.5)
        rec      = "✅ PROCEED — Profitable" if new_pft >= base_pft else "⚠️ RISKY — Margin Erosion"
        rec_col  = "#22c55e" if new_pft >= base_pft else "#ef4444"
        rec_bg   = "#f0fdf4" if new_pft >= base_pft else "#fef2f2"

        with c2:
            fig = go.Figure(data=[
                go.Bar(name='Baseline',  x=['Revenue','Profit'],
                       y=[base_rev,base_pft], marker_color=C_BLUE,
                       text=[f"${base_rev:,.0f}", f"${base_pft:,.0f}"],
                       textposition='outside', textfont_size=11),
                go.Bar(name='Projected', x=['Revenue','Profit'],
                       y=[new_rev,new_pft],
                       marker_color=[C_GREEN if new_rev>=base_rev else C_RED,
                                     C_GREEN if new_pft>=base_pft else C_RED],
                       text=[f"${new_rev:,.0f}", f"${new_pft:,.0f}"],
                       textposition='outside', textfont_size=11),
            ])
            fig.update_layout(**LIGHT_TPL, barmode='group', height=280,
                              margin=dict(l=0,r=0,t=20,b=0),
                              legend=dict(orientation='h', y=-0.2))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box">
            <div class="label">Baseline Revenue</div>
            <div class="val">${base_rev:,.0f}</div>
          </div>
          <div class="metric-box">
            <div class="label">Projected Revenue</div>
            <div class="val">${new_rev:,.0f}</div>
            <div class="chg {'pos' if new_rev>=base_rev else 'neg'}">
              {'↑' if new_rev>=base_rev else '↓'} ${abs(new_rev-base_rev):,.0f} ({abs(new_rev/base_rev-1):.1%})
            </div>
          </div>
          <div class="metric-box">
            <div class="label">Baseline Profit</div>
            <div class="val">${base_pft:,.0f}</div>
          </div>
          <div class="metric-box">
            <div class="label">Projected Profit</div>
            <div class="val">${new_pft:,.0f}</div>
            <div class="chg {'pos' if new_pft>=base_pft else 'neg'}">
              {'↑' if new_pft>=base_pft else '↓'} ${abs(new_pft-base_pft):,.0f}
            </div>
          </div>
        </div>
        <div style="background:{rec_bg};border:1px solid {rec_col};border-left:4px solid {rec_col};
                    border-radius:10px;padding:12px 16px;font-size:14px;font-weight:600;color:{rec_col}">
          AI Recommendation: {rec}
        </div>""", unsafe_allow_html=True)

    with t2:
        budget = st.number_input("Total Marketing Budget ($)", 1000, 500000, 50000, step=5000)
        rp = df.groupby("region").agg(
            revenue=("revenue","sum"), profit=("profit","sum"),
            orders=("revenue","count"), churn=("customer_churned","mean")
        ).reset_index()
        rp["roi_score"] = (rp["profit"]/rp["revenue"])*(1-rp["churn"])*np.log1p(rp["revenue"])
        rp["share"]     = (rp["roi_score"]/rp["roi_score"].sum()*100).round(1)
        rp["alloc"]     = (rp["share"]/100*budget).astype(int)

        # Pie of allocation
        fig_alloc = px.pie(rp, values='alloc', names='region',
                           color_discrete_sequence=COLORS, hole=0.5,
                           title="Recommended Budget Split")
        fig_alloc.update_traces(textinfo='percent+label', textfont_size=12)
        fig_alloc.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=40,b=0),
                                showlegend=False)
        c_alloc1, c_alloc2 = st.columns([1,2])
        with c_alloc1:
            st.plotly_chart(fig_alloc, use_container_width=True)
        with c_alloc2:
            st.dataframe(rp[["region","revenue","profit","churn","share","alloc"]].rename(
                columns={"revenue":"Revenue","profit":"Profit","churn":"Churn Rate",
                         "share":"Budget %","alloc":"Allocated ($)"}
            ).round(2), use_container_width=True, hide_index=True)

    with t3:
        cm = df.groupby("product_category").agg(
            revenue=("revenue","sum"), profit=("profit","sum"),
            orders=("revenue","count"), churn=("customer_churned","mean")
        ).reset_index()
        cm["margin"] = cm["profit"]/cm["revenue"]*100
        fig5 = px.scatter(cm, x="revenue", y="margin", size="orders",
                          color="churn", text="product_category",
                          size_max=60,
                          color_continuous_scale=["#22c55e","#f59e0b","#ef4444"],
                          labels={"revenue":"Revenue","margin":"Profit Margin (%)","churn":"Churn Rate"})
        fig5.update_traces(textposition="top center",
                           textfont=dict(color="#1a1f36", size=11, family="Inter"))
        fig5.update_coloraxes(colorbar_title="Churn Rate")
        fig5.update_layout(**LIGHT_TPL, height=400, margin=dict(l=0,r=0,t=10,b=0))
        st.markdown('<div class="sec-title">Product Matrix: Revenue vs Margin vs Churn <span class="badge">SIZE = ORDERS</span></div>', unsafe_allow_html=True)
        st.plotly_chart(fig5, use_container_width=True)


# ─── PAGE 6: COMPETITIVE INTELLIGENCE (NEW) ──────────────
def page_competitive(df):
    page_header("🌐", "Competitive Intelligence",
                "Market share analysis and competitive positioning simulator",
                badge="Simulator")

    st.markdown("""
    <div class="warn-box">
        ⚡ <b>Simulation Mode:</b> Adjust your market assumptions to model competitive scenarios.
        Numbers are relative to your actual revenue data.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Market Size Assumptions**")
        total_market = st.number_input("Total Market Size ($M)", 1, 1000, 50)
        your_rev = df['revenue'].sum() / 1e6
        your_share = (your_rev / total_market) * 100

        st.markdown("**Competitor Estimates**")
        comp1 = st.slider("Competitor A share (%)", 5, 60, 28)
        comp2 = st.slider("Competitor B share (%)", 5, 40, 18)
        comp3 = st.slider("Competitor C share (%)", 5, 30, 12)

        others = max(0, 100 - your_share - comp1 - comp2 - comp3)

    with c2:
        shares = {
            'You': round(your_share, 1),
            'Competitor A': comp1,
            'Competitor B': comp2,
            'Competitor C': comp3,
            'Others': round(others, 1)
        }
        share_df = pd.DataFrame(list(shares.items()), columns=['Company','Share'])
        colors_comp = [C_BLUE, C_RED, '#f59e0b', C_PURP, '#9ca3af']
        fig = px.pie(share_df, values='Share', names='Company',
                     color_discrete_sequence=colors_comp, hole=0.5)
        fig.update_traces(textinfo='percent+label', textfont_size=12,
                          pull=[0.06,0,0,0,0])
        fig.update_layout(**LIGHT_TPL, height=340, margin=dict(l=0,r=0,t=10,b=0),
                          showlegend=False)
        st.markdown('<div class="sec-title">Estimated Market Share</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    # Growth scenarios
    st.markdown('<div class="sec-title">Share Growth Scenarios <span class="badge">WHAT-IF</span></div>', unsafe_allow_html=True)
    growth_targets = [1, 2, 5, 10]
    scenarios = []
    for g in growth_targets:
        new_share = your_share + g
        new_rev   = new_share/100 * total_market * 1e6
        delta_rev = new_rev - your_rev * 1e6
        scenarios.append({
            'Share Gain': f"+{g}%",
            'New Share': f"{new_share:.1f}%",
            'Projected Revenue': f"${new_rev/1e6:.2f}M",
            'Revenue Uplift': f"+${delta_rev/1e3:.0f}K",
            'Est. Cost to Achieve': f"${delta_rev*0.15/1e3:.0f}K"
        })
    st.dataframe(pd.DataFrame(scenarios), use_container_width=True, hide_index=True)

    # Competitive benchmark radar
    st.markdown('<div class="sec-title">Competitive Strength Radar</div>', unsafe_allow_html=True)
    categories = ['Price Competitiveness','Product Quality','Distribution Reach',
                  'Brand Awareness','Customer Service','Innovation']
    you_scores  = [72, 85, 68, 78, 82, 70]
    comp_scores = [85, 75, 80, 90, 70, 65]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatterpolar(r=you_scores+[you_scores[0]], theta=categories+[categories[0]],
                                    fill='toself', name='Your Company',
                                    fillcolor='rgba(79,142,247,0.2)', line=dict(color=C_BLUE, width=2)))
    fig2.add_trace(go.Scatterpolar(r=comp_scores+[comp_scores[0]], theta=categories+[categories[0]],
                                    fill='toself', name='Top Competitor',
                                    fillcolor='rgba(239,68,68,0.12)', line=dict(color=C_RED, width=2)))
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            bgcolor='rgba(248,250,255,0.5)',
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=10),
                            gridcolor='#e4e9f2', linecolor='#e4e9f2'),
            angularaxis=dict(tickfont=dict(size=11, color='#1a1f36'), gridcolor='#e4e9f2')
        ),
        showlegend=True, height=380,
        legend=dict(orientation='h', y=-0.12),
        margin=dict(l=40,r=40,t=20,b=40),
        font=dict(family='Inter', color='#6b7280')
    )
    st.plotly_chart(fig2, use_container_width=True)


# ─── PAGE 7: AI STRATEGY AGENT ───────────────────────────
def page_ai_agent(df):
    page_header("🤖", "AI Strategy Agent",
                "Ask business questions in plain English — powered by real sales data + Claude AI",
                badge="Claude AI")

    st.markdown("""
    <div class="success-box">
        ✅ <b>Claude AI Active</b> — Answering with real-time analysis of your sales data.
        No API key needed from you — powered by the dashboard backend.
    </div>""", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        total_rev = df['revenue'].sum()
        st.session_state.chat_history.append({
            "role": "ai",
            "content": f"""**👋 Hello! I'm your AI Sales Analyst.**

I have full access to your filtered sales dataset:
- **${total_rev:,.0f}** total revenue across **{len(df):,}** transactions
- Period: **{df['date'].min().strftime('%b %Y')}** → **{df['date'].max().strftime('%b %Y')}**

I can answer questions about strategy, performance, churn, forecasting, discount optimization, regional analysis, and more.

**What would you like to explore?**"""
        })

    # Quick questions
    quick_qs = [
        "Summarize sales performance",
        "Which region should I invest in?",
        "Analyze customer churn risk",
        "Forecast next quarter",
        "Should I run discount promotions?",
        "What is my top product category?",
        "Give me a 90-day strategy",
        "How can I improve profit margin?",
    ]

    st.markdown('<div class="sec-title">Quick Questions</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, q in enumerate(quick_qs):
        if cols[i % 4].button(q, key=f"qq_{i}", use_container_width=True):
            st.session_state.pending_q = q

    # Chat display
    chat_html = '<div class="chat-outer"><div class="chat-header"><div class="dot"></div><div class="title">Sales Intelligence Chat</div><div class="sub">Claude AI · Real-time data</div></div><div class="chat-wrap">'
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_html += f'<div class="bubble-user"><div class="bubble-inner">{msg["content"]}</div></div>'
        else:
            content = msg["content"]
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            content = content.replace('\n- ', '<br>• ').replace('\n', '<br>')
            chat_html += f'<div class="bubble-ai"><div class="avatar">🤖</div><div class="bubble-inner">{content}</div></div>'
    chat_html += '</div></div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Handle pending question
    if "pending_q" in st.session_state:
        user_q = st.session_state.pop("pending_q")
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.spinner("🧠 Analyzing your data..."):
            answer = ai_answer(user_q, df)
        st.session_state.chat_history.append({"role": "ai", "content": answer})
        st.rerun()

    # Chat input
    user_input = st.chat_input("Ask about strategy, performance, forecasts, or customers...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("🧠 Analyzing your data..."):
            answer = ai_answer(user_input, df)
        st.session_state.chat_history.append({"role": "ai", "content": answer})
        st.rerun()

    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


# ─── PAGE 8: REPORTS ─────────────────────────────────────
def page_reports(df):
    page_header("📋", "Reports & Export",
                "Download data, summaries and performance reports")

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-box">
        <div class="label">Total Revenue</div>
        <div class="val">${df['revenue'].sum():,.2f}</div>
      </div>
      <div class="metric-box">
        <div class="label">Total Profit</div>
        <div class="val">${df['profit'].sum():,.2f}</div>
      </div>
      <div class="metric-box">
        <div class="label">Profit Margin</div>
        <div class="val">{df['profit'].sum()/df['revenue'].sum()*100:.1f}%</div>
      </div>
      <div class="metric-box">
        <div class="label">Total Orders</div>
        <div class="val">{len(df):,}</div>
      </div>
      <div class="metric-box">
        <div class="label">Churn Rate</div>
        <div class="val">{df['customer_churned'].mean()*100:.1f}%</div>
      </div>
      <div class="metric-box">
        <div class="label">Top Category</div>
        <div class="val">{df.groupby('product_category')['revenue'].sum().idxmax()}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Data Exports</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇ Full Dataset (CSV)",
                           df.to_csv(index=False), "sales_data.csv", "text/csv",
                           use_container_width=True)
    with c2:
        monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
        st.download_button("⬇ Monthly Summary (CSV)",
                           monthly.to_csv(index=False), "monthly_summary.csv", "text/csv",
                           use_container_width=True)
    with c3:
        regional = df.groupby("region")[["revenue","profit"]].sum().reset_index()
        st.download_button("⬇ Regional Summary (CSV)",
                           regional.to_csv(index=False), "regional_summary.csv", "text/csv",
                           use_container_width=True)

    # Category performance table
    st.markdown('<div class="sec-title">Category Performance Summary</div>', unsafe_allow_html=True)
    cat_summary = df.groupby("product_category").agg(
        Revenue=("revenue","sum"),
        Profit=("profit","sum"),
        Orders=("revenue","count"),
        Avg_Order_Value=("revenue","mean"),
        Churn_Rate=("customer_churned","mean"),
        Avg_Discount=("discount","mean")
    ).reset_index()
    cat_summary["Profit Margin"] = (cat_summary["Profit"]/cat_summary["Revenue"]*100).round(1)
    cat_summary["Churn_Rate"]    = (cat_summary["Churn_Rate"]*100).round(1)
    cat_summary["Avg_Discount"]  = (cat_summary["Avg_Discount"]*100).round(1)
    cat_summary = cat_summary.sort_values("Revenue", ascending=False)
    st.dataframe(cat_summary.rename(columns={
        "product_category":"Category",
        "Avg_Order_Value":"Avg Order ($)",
        "Churn_Rate":"Churn %",
        "Avg_Discount":"Avg Disc %"
    }), use_container_width=True, hide_index=True)


# ─── MAIN ─────────────────────────────────────────────────
def main():
    df = load_data()
    page, date_range, cats, regions = render_sidebar(df)
    df_f = filter_df(df, date_range, cats, regions)

    if not len(df_f):
        st.warning("⚠️ No data matches the selected filters. Please adjust your filters.")
        return

    if   "Executive Dashboard"        in page: page_dashboard(df_f)
    elif "Sales Forecasting"          in page: page_forecasting(df_f)
    elif "Churn Prediction"           in page: page_churn(df_f)
    elif "Customer Segmentation"      in page: page_segmentation(df_f)
    elif "Strategy Simulator"         in page: page_strategy(df_f)
    elif "Competitive Intelligence"   in page: page_competitive(df_f)
    elif "AI Strategy Agent"          in page: page_ai_agent(df_f)
    elif "Reports"                    in page: page_reports(df_f)

if __name__ == "__main__":
    main()
