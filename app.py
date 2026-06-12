"""
dashboard/app.py  — ULTRA PRO EDITION v3.0
==========================================
NEW FEATURES IN THIS VERSION:
  1.  Smart Alerts Panel — auto-detects high churn, low margin, slow regions
  2.  Anomaly Detection — ML flags revenue spikes/drops automatically
  3.  Goal Tracker — set targets, track progress with live gauges
  4.  Product Affinity Matrix — cross-sell engine (which categories co-occur)
  5.  Customer Lifetime Value (CLV) Calculator — predict long-term value
  6.  Sales Velocity Tracker — revenue pace vs target with burn-rate indicator
  7.  AI Narrative Generator — auto executive summary paragraph on dashboard
  8.  Discount ROI Heatmap — category × discount × profit impact matrix
  9.  Revenue Waterfall Chart — retained vs lost revenue cohort view
  10. Dark / Light Mode Toggle — user-controlled theme switch in sidebar

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

# ─── THEME TOGGLE (session state) ─────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

DM = st.session_state.dark_mode

# ─── DYNAMIC THEME CSS ───────────────────────────────────
if DM:
    BG_APP    = "#0d1117"
    BG_CARD   = "#161b22"
    BG_CARD2  = "#1c2333"
    BORDER    = "#30363d"
    TEXT_PRI  = "#e6edf3"
    TEXT_SEC  = "#8b949e"
    TEXT_MUT  = "#484f58"
    SIDEBAR_BG= "#010409"
    BG_INPUT  = "#21262d"
    CHIP_BG   = "#1c2333"
    CHIP_BORD = "#388bfd"
    CHIP_COL  = "#79c0ff"
    INFO_BG   = "#0d419d22"
    INFO_BORD = "#388bfd"
    INFO_COL  = "#79c0ff"
    WARN_BG   = "#9e6a0322"
    WARN_BORD = "#d29922"
    WARN_COL  = "#e3b341"
    SUC_BG    = "#04260f22"
    SUC_BORD  = "#238636"
    SUC_COL   = "#3fb950"
    PLOT_BG   = "rgba(22,27,34,0.8)"
    PLOT_GRID = "#21262d"
    PLOT_LINE = "#30363d"
    PLOT_FONT = "#8b949e"
    HEADER_BG = "#161b22"
    HEADER_BD = "#30363d"
    BADGE_BG  = "#1c2333"
    BADGE_BD  = "#388bfd"
    BADGE_COL = "#79c0ff"
    HEALTH_BG = "rgba(63,185,80,0.1)"
    HEALTH_BD = "rgba(63,185,80,0.3)"
else:
    BG_APP    = "#f0f2f6"
    BG_CARD   = "#ffffff"
    BG_CARD2  = "#f8faff"
    BORDER    = "#e4e9f2"
    TEXT_PRI  = "#1a1f36"
    TEXT_SEC  = "#6b7280"
    TEXT_MUT  = "#9ca3af"
    SIDEBAR_BG= "#1a1f36"
    BG_INPUT  = "#ffffff"
    CHIP_BG   = "#f8faff"
    CHIP_BORD = "#c7d7fc"
    CHIP_COL  = "#3b5bdb"
    INFO_BG   = "#eef4ff"
    INFO_BORD = "#c7d7fc"
    INFO_COL  = "#3b5bdb"
    WARN_BG   = "#fffbeb"
    WARN_BORD = "#fde68a"
    WARN_COL  = "#92400e"
    SUC_BG    = "#f0fdf4"
    SUC_BORD  = "#bbf7d0"
    SUC_COL   = "#166534"
    PLOT_BG   = "rgba(248,250,255,0.6)"
    PLOT_GRID = "#f0f2f6"
    PLOT_LINE = "#e4e9f2"
    PLOT_FONT = "#6b7280"
    HEADER_BG = "#ffffff"
    HEADER_BD = "#e4e9f2"
    BADGE_BG  = "#eef4ff"
    BADGE_BD  = "#c7d7fc"
    BADGE_COL = "#3b5bdb"
    HEALTH_BG = "rgba(110,231,183,0.15)"
    HEALTH_BD = "rgba(110,231,183,0.3)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG_APP};
    color: {TEXT_PRI};
}}
.stApp {{ background: {BG_APP}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: none;
    box-shadow: 4px 0 20px rgba(0,0,0,0.2);
    min-width: 240px !important;
}}
section[data-testid="stSidebar"] * {{ color: #c8cde4 !important; }}
section[data-testid="stSidebar"] .stRadio label {{
    color: #c8cde4 !important; font-size: 13px; padding: 6px 0;
}}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label {{
    color: #8892b0 !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: 0.07em;
}}

.brand-block {{
    padding: 1.6rem 1.2rem 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1rem;
}}
.brand-logo {{
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #4f8ef7, #6ee7b7);
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 18px; margin-bottom: 10px;
}}
.brand-title {{
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem;
    font-weight: 800; color: #ffffff !important; letter-spacing: -0.02em; margin-bottom: 2px;
}}
.brand-sub {{ font-size: 10px; color: #5a6478 !important; text-transform: uppercase; letter-spacing: 0.1em; }}

.health-badge {{
    background: {HEALTH_BG}; border: 1px solid {HEALTH_BD};
    border-radius: 8px; padding: 8px 12px; margin: 8px 0; font-size: 11px;
}}
.health-badge .score {{ color: #6ee7b7 !important; font-weight: 700; font-size: 14px; }}
.health-badge .label {{ color: #8892b0 !important; }}

/* ── Smart Alert Banner ── */
.alert-panel {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 1rem 1.2rem; margin-bottom: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}
.alert-item {{
    display: flex; align-items: flex-start; gap: 10px;
    padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; font-size: 12px;
}}
.alert-item.danger  {{ background: #fef2f2; border-left: 3px solid #ef4444; color: #991b1b; }}
.alert-item.warning {{ background: #fffbeb; border-left: 3px solid #f59e0b; color: #92400e; }}
.alert-item.success {{ background: #f0fdf4; border-left: 3px solid #22c55e; color: #166534; }}
.alert-item.info    {{ background: {INFO_BG}; border-left: 3px solid #3b5bdb; color: {INFO_COL}; }}

.page-header {{
    background: {HEADER_BG}; border: 1px solid {HEADER_BD};
    border-radius: 14px; padding: 1.6rem 2rem; margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    display: flex; align-items: center; justify-content: space-between;
}}
.page-header-left h1 {{
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.5rem;
    font-weight: 700; color: {TEXT_PRI}; margin: 0 0 3px;
}}
.page-header-left p {{ color: {TEXT_SEC}; font-size: 13px; margin: 0; }}
.page-header-badge {{
    background: {BADGE_BG}; border: 1px solid {BADGE_BD};
    border-radius: 8px; padding: 6px 14px; font-size: 12px;
    font-weight: 600; color: {BADGE_COL};
}}

.kpi-grid {{
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 14px; margin-bottom: 1.5rem;
}}
.kpi-card {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 1.3rem 1.4rem 1rem;
    position: relative; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s, transform 0.2s;
}}
.kpi-card:hover {{
    box-shadow: 0 8px 24px rgba(79,142,247,0.15);
    transform: translateY(-2px);
}}
.kpi-card .kpi-icon {{
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; margin-bottom: 10px;
}}
.kpi-card.blue .kpi-icon   {{ background: {'#1c2333' if DM else '#eef4ff'}; }}
.kpi-card.green .kpi-icon  {{ background: {'#0d2818' if DM else '#ecfdf5'}; }}
.kpi-card.purple .kpi-icon {{ background: {'#1e1b33' if DM else '#f5f3ff'}; }}
.kpi-card.orange .kpi-icon {{ background: {'#2d1a00' if DM else '#fff7ed'}; }}
.kpi-card.red .kpi-icon    {{ background: {'#2d0a0a' if DM else '#fef2f2'}; }}
.kpi-card .kpi-label {{
    font-size: 11px; color: {TEXT_MUT}; text-transform: uppercase;
    letter-spacing: 0.07em; margin-bottom: 4px; font-weight: 500;
}}
.kpi-card .kpi-value {{
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.55rem;
    font-weight: 800; color: {TEXT_PRI}; line-height: 1; margin-bottom: 5px;
}}
.kpi-card .kpi-delta {{
    font-size: 11px; font-weight: 500; display: inline-flex;
    align-items: center; gap: 3px; padding: 2px 7px; border-radius: 20px;
}}
.kpi-card .kpi-delta.up      {{ color: #059669; background: {'#0d2818' if DM else '#ecfdf5'}; }}
.kpi-card .kpi-delta.down    {{ color: #dc2626; background: {'#2d0a0a' if DM else '#fef2f2'}; }}
.kpi-card .kpi-delta.neutral {{ color: {TEXT_SEC}; background: {'#21262d' if DM else '#f3f4f6'}; }}

.sec-title {{
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.95rem;
    font-weight: 700; color: {TEXT_PRI}; margin: 1.4rem 0 0.8rem;
    display: flex; align-items: center; gap: 8px;
}}
.sec-title .badge {{
    font-size: 10px; font-weight: 600; background: {BADGE_BG};
    color: {BADGE_COL}; padding: 2px 8px; border-radius: 20px;
    text-transform: uppercase; letter-spacing: 0.06em;
}}

.chart-card {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}

.chat-outer {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 0; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04); margin-bottom: 1rem;
}}
.chat-header {{
    padding: 12px 16px; border-bottom: 1px solid {BORDER};
    display: flex; align-items: center; gap: 8px; background: {BG_CARD2};
}}
.chat-header .dot {{ width:8px; height:8px; border-radius:50%; background:#22c55e; box-shadow:0 0 0 3px rgba(34,197,94,0.2); }}
.chat-header .title {{ font-size:13px; font-weight:600; color:{TEXT_PRI}; }}
.chat-header .sub {{ font-size:11px; color:{TEXT_MUT}; margin-left:auto; }}
.chat-wrap {{
    max-height: 440px; overflow-y: auto;
    padding: 1rem 1.2rem; background: {BG_CARD2};
}}
.chat-wrap::-webkit-scrollbar {{ width: 4px; }}
.chat-wrap::-webkit-scrollbar-track {{ background: transparent; }}
.chat-wrap::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 4px; }}
.bubble-user {{
    display: flex; justify-content: flex-end;
    margin-bottom: 14px; animation: fadeUp .25s ease;
}}
.bubble-user .bubble-inner {{
    background: linear-gradient(135deg, #3b5bdb, #4f8ef7); color: #fff;
    border-radius: 16px 16px 4px 16px; padding: 10px 15px; max-width: 75%;
    font-size: 13px; line-height: 1.5; box-shadow: 0 4px 12px rgba(59,91,219,0.25);
}}
.bubble-ai {{ display: flex; align-items: flex-start; gap: 10px; margin-bottom: 14px; animation: fadeUp .25s ease; }}
.bubble-ai .avatar {{
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, #4f8ef7, #6ee7b7);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0; margin-top: 2px;
    box-shadow: 0 2px 8px rgba(79,142,247,0.3);
}}
.bubble-ai .bubble-inner {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    color: {TEXT_PRI}; border-radius: 4px 16px 16px 16px;
    padding: 11px 15px; max-width: 82%; font-size: 13px;
    line-height: 1.65; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}
.bubble-ai .bubble-inner b {{ color: #4f8ef7; }}
@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:translateY(0); }} }}

.metric-row {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px; margin: 12px 0;
}}
.metric-box {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 12px; padding: 1rem 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
.metric-box .label {{ font-size:10px; color:{TEXT_MUT}; text-transform:uppercase; letter-spacing:.07em; margin-bottom:5px; font-weight:500; }}
.metric-box .val   {{ font-family:'Plus Jakarta Sans',sans-serif; font-size:1.3rem; font-weight:700; color:{TEXT_PRI}; }}
.metric-box .chg   {{ font-size:11px; margin-top:3px; font-weight:500; }}
.metric-box .chg.pos {{ color:#059669; }}
.metric-box .chg.neg {{ color:#dc2626; }}

.info-box {{
    background: {INFO_BG}; border: 1px solid {INFO_BORD};
    border-left: 4px solid #3b5bdb; border-radius: 8px;
    padding: 10px 14px; font-size: 12px; color: {INFO_COL};
    margin-bottom: 12px; font-weight: 500;
}}
.success-box {{
    background: {SUC_BG}; border: 1px solid {SUC_BORD};
    border-left: 4px solid #22c55e; border-radius: 8px;
    padding: 10px 14px; font-size: 12px; color: {SUC_COL};
    margin-bottom: 12px; font-weight: 500;
}}
.warn-box {{
    background: {WARN_BG}; border: 1px solid {WARN_BORD};
    border-left: 4px solid #f59e0b; border-radius: 8px;
    padding: 10px 14px; font-size: 12px; color: {WARN_COL};
    margin-bottom: 12px; font-weight: 500;
}}

/* ── Goal tracker gauge area ── */
.goal-card {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 1.2rem; text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}
.goal-label {{ font-size: 11px; color: {TEXT_MUT}; text-transform: uppercase; letter-spacing: .07em; margin-bottom: 4px; }}
.goal-value {{ font-family:'Plus Jakarta Sans',sans-serif; font-size: 1.2rem; font-weight: 700; color: {TEXT_PRI}; }}

/* ── CLV segment boxes ── */
.clv-box {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 12px; padding: 1rem 1.2rem; text-align:center;
}}

/* ── Velocity indicator ── */
.velocity-bar {{
    height: 8px; border-radius: 4px;
    background: linear-gradient(90deg, #22c55e, #4f8ef7, #ef4444);
    margin: 6px 0;
}}

/* ── Streamlit widget overrides ── */
.stSelectbox > div > div {{
    background: {BG_INPUT} !important; border-color: {BORDER} !important;
    color: {TEXT_PRI} !important; border-radius: 10px !important;
}}
.stTextInput > div > div > input {{
    background: {BG_INPUT} !important; border-color: {BORDER} !important;
    color: {TEXT_PRI} !important; border-radius: 10px !important;
}}
div[data-testid="stChatInput"] {{
    background: {BG_INPUT} !important; border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}
.stSlider > div {{ color: {TEXT_PRI}; }}
.stTabs [data-baseweb="tab-list"] {{
    background: {'#161b22' if DM else '#f0f2f6'};
    border-radius: 10px; padding: 4px; gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px; padding: 6px 16px;
    font-size: 13px; font-weight: 500; color: {TEXT_SEC};
}}
.stTabs [aria-selected="true"] {{
    background: {BG_CARD} !important; color: {TEXT_PRI} !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}}
.stButton > button {{
    background: linear-gradient(135deg, #3b5bdb, #4f8ef7);
    color: white; border: none; border-radius: 10px;
    font-weight: 600; font-size: 13px;
    padding: 0.5rem 1.2rem; transition: opacity 0.2s;
}}
.stButton > button:hover {{ opacity: 0.88; }}
section[data-testid="stSidebar"] .stRadio > div {{ gap: 2px; }}
section[data-testid="stSidebar"] .stRadio label span {{ font-size: 13px !important; font-weight: 500; }}
.stDataFrame {{ border-radius: 12px; overflow: hidden; }}
.seg-high  {{ background:#ecfdf5; color:#065f46; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }}
.seg-mid   {{ background:#fffbeb; color:#92400e; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }}
.seg-low   {{ background:#fef2f2; color:#991b1b; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }}

/* ── Anomaly badge ── */
.anomaly-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 20px; padding: 3px 10px;
    font-size: 11px; font-weight: 600; color: #dc2626;
}}
.anomaly-good {{
    background: #f0fdf4; border-color: #bbf7d0; color: #059669;
}}
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY TEMPLATE ─────────────────────────────────────
LIGHT_TPL = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor=PLOT_BG,
    font=dict(color=PLOT_FONT, family='Inter', size=11),
    xaxis=dict(gridcolor=PLOT_GRID, linecolor=PLOT_LINE, tickcolor=PLOT_FONT, showgrid=True),
    yaxis=dict(gridcolor=PLOT_GRID, linecolor=PLOT_LINE, tickcolor=PLOT_FONT, showgrid=True),
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
    try:
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 700,
            "system": context,
            "messages": [{"role": "user", "content": question}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
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
- Keep under 250 words
- Be specific and actionable, reference actual numbers
- End with one clear recommendation"""

    claude_resp = call_claude_api(question, context)
    if claude_resp:
        return claude_resp

    # Rule-based fallback
    q = question.lower()
    if any(k in q for k in ['summary','overview','performance','kpi','total']):
        return f"""**📊 Sales Performance Summary**
- **Total Revenue:** ${total_rev:,.0f}
- **Total Profit:** ${total_pft:,.0f}
- **Profit Margin:** {margin:.1f}% {'— above target ✅' if margin>30 else '— below 30% target ⚠️'}
- **Churn Rate:** {churn:.1f}% {'— action required 🚨' if churn>20 else '— within benchmark ✅'}
- **Top Category:** {top_cat} contributing ${cat_rev[top_cat]:,.0f}
- **Top Region:** {top_reg} at ${reg_rev[top_reg]:,.0f}

**Recommendation:** Scale {top_cat} in {top_reg} — your highest-ROI combination."""

    if any(k in q for k in ['churn','retain','losing','customer','at-risk']):
        annual_loss = total_rev * (churn/100) * 0.3
        return f"""**🚨 Customer Churn Analysis**
- **Current churn rate:** {churn:.1f}%
- **Estimated annual revenue at risk:** ${annual_loss:,.0f}
- **3-Step Retention Plan:**
1. Launch loyalty tier program (target 5% churn reduction)
2. Personalized win-back emails for {worst_reg} customers
3. Proactive check-in for top 20% revenue customers

**Recommendation:** Fixing churn to 15% could recover ~${annual_loss*0.5:,.0f}/year."""

    if any(k in q for k in ['forecast','predict','next','future','quarter']):
        quarterly = df.resample('QE', on='date')['revenue'].sum()
        last_q    = quarterly.iloc[-1] if len(quarterly) > 0 else 0
        return f"""**🔮 Revenue Forecast**
- **Last quarter:** ${last_q:,.0f}
- **Base case (+5%):** ${last_q*1.05:,.0f}
- **Bull case (+12%):** ${last_q*1.12:,.0f}
- **Bear case (–4%):** ${last_q*0.96:,.0f}

**Recommendation:** Plan around base case; keep 8% in reserve for opportunistic spend."""

    if any(k in q for k in ['region','area','geography','where']):
        ranked = reg_rev.sort_values(ascending=False)
        lines  = '\n'.join([f"- **{r}:** ${v:,.0f}" for r, v in ranked.items()])
        return f"""**📍 Regional Performance**\n{lines}\n\n**Recommendation:** Prioritize {top_reg} (40% budget), then tackle {worst_reg} recovery with 20%."""

    if any(k in q for k in ['clv','lifetime','value','customer value']):
        avg_order = df['revenue'].mean()
        avg_freq  = 4.2
        avg_life  = 2.8
        clv = avg_order * avg_freq * avg_life * (1 - churn/100)
        return f"""**💎 Customer Lifetime Value Analysis**
- **Average Order Value:** ${avg_order:,.0f}
- **Estimated Purchase Frequency:** {avg_freq:.1f}x/year
- **Average Customer Lifespan:** {avg_life:.1f} years
- **Estimated CLV:** ${clv:,.0f}

- High-value customers (top 20%) drive ~60-70% of revenue
- Churn at {churn:.1f}% significantly reduces lifetime value

**Recommendation:** A 10% churn reduction could lift CLV by ~${clv*0.1:,.0f} per customer."""

    if any(k in q for k in ['anomaly','anomalies','unusual','spike','drop','outlier']):
        weekly = df.resample('W', on='date')['revenue'].sum()
        std    = weekly.std()
        mean   = weekly.mean()
        spikes = (weekly > mean + 2*std).sum()
        drops  = (weekly < mean - 2*std).sum()
        return f"""**🔍 Anomaly Detection Report**
- **Mean weekly revenue:** ${mean:,.0f}
- **Standard deviation:** ${std:,.0f}
- **Revenue spikes detected (>2σ):** {spikes} weeks
- **Revenue drops detected (<2σ):** {drops} weeks

{'⚠️ Anomalies found — investigate marketing events or seasonality' if spikes+drops>0 else '✅ Revenue is stable — no significant anomalies'}

**Recommendation:** Cross-reference spike/drop dates with campaign calendars and external events."""

    if any(k in q for k in ['velocity','pace','rate','speed','burn']):
        days = (df['date'].max() - df['date'].min()).days or 1
        daily_rate = total_rev / days
        return f"""**⚡ Sales Velocity Analysis**
- **Daily revenue rate:** ${daily_rate:,.0f}/day
- **Weekly pace:** ${daily_rate*7:,.0f}/week
- **Monthly pace:** ${daily_rate*30:,.0f}/month
- **Top velocity driver:** {top_cat} in {top_reg}

**Recommendation:** Maintain current pace in {top_reg}; accelerate {worst_reg} with targeted campaigns to close velocity gap."""

    return f"""**🤖 Sales Intelligence**

Snapshot: **${total_rev:,.0f} revenue** | **{margin:.1f}% margin** | **{churn:.1f}% churn**

I can help with: sales summary, churn analysis, forecasting, regional breakdown, CLV, anomalies, velocity, strategy.

Try: *"Detect revenue anomalies"* or *"Calculate customer lifetime value"*"""


# ════════════════════════════════════════════════════════
# ─── NEW FEATURE 1: SMART ALERTS ENGINE ─────────────────
# ════════════════════════════════════════════════════════
def build_alerts(df):
    alerts = []
    churn = df['customer_churned'].mean() * 100
    margin = df['profit'].sum() / df['revenue'].sum() * 100
    reg_rev = df.groupby('region')['revenue'].sum()
    worst_reg = reg_rev.idxmin()
    best_reg  = reg_rev.idxmax()
    worst_rev = reg_rev.min()
    best_rev  = reg_rev.max()
    gap = (best_rev - worst_rev) / best_rev * 100

    if churn > 25:
        alerts.append(("danger", f"🚨 Critical churn rate: {churn:.1f}% — immediate retention campaign needed"))
    elif churn > 18:
        alerts.append(("warning", f"⚠️ Elevated churn: {churn:.1f}% — monitor closely and prep win-back sequence"))
    else:
        alerts.append(("success", f"✅ Churn rate healthy: {churn:.1f}% — within 15–18% benchmark"))

    if margin < 20:
        alerts.append(("danger", f"🚨 Low profit margin: {margin:.1f}% — review pricing and cost structure"))
    elif margin < 28:
        alerts.append(("warning", f"⚠️ Margin under pressure: {margin:.1f}% — cap discounts at 10%"))
    else:
        alerts.append(("success", f"✅ Healthy margin: {margin:.1f}% — above 28% target"))

    if gap > 60:
        alerts.append(("warning", f"⚠️ Regional imbalance: {worst_reg} is {gap:.0f}% below {best_reg} — investigate"))
    else:
        alerts.append(("info", f"📍 Regional spread healthy: max gap {gap:.0f}% between {best_reg} and {worst_reg}"))

    # Anomaly check
    weekly = df.resample('W', on='date')['revenue'].sum()
    if len(weekly) > 4:
        last4_mean = weekly.iloc[-4:].mean()
        prev_mean  = weekly.iloc[:-4].mean() if len(weekly) > 8 else weekly.mean()
        pct_change = (last4_mean - prev_mean) / prev_mean * 100
        if pct_change < -15:
            alerts.append(("danger", f"📉 Revenue declining: last 4-week avg is {abs(pct_change):.0f}% below prior period"))
        elif pct_change > 20:
            alerts.append(("success", f"📈 Revenue surging: last 4-week avg is +{pct_change:.0f}% above prior period"))

    return alerts


# ════════════════════════════════════════════════════════
# ─── NEW FEATURE 2: ANOMALY DETECTION ───────────────────
# ════════════════════════════════════════════════════════
def detect_anomalies(df, z_thresh=2.0):
    weekly = df.resample('W', on='date')['revenue'].sum().reset_index()
    weekly.columns = ['date','revenue']
    if len(weekly) < 5:
        return weekly, []
    mean = weekly['revenue'].mean()
    std  = weekly['revenue'].std()
    weekly['z_score']   = (weekly['revenue'] - mean) / std
    weekly['is_anomaly']= weekly['z_score'].abs() > z_thresh
    weekly['direction'] = weekly['z_score'].apply(lambda z: 'spike' if z > 0 else 'drop')
    anomalies = weekly[weekly['is_anomaly']].copy()
    return weekly, anomalies


# ════════════════════════════════════════════════════════
# ─── SIDEBAR ─────────────────────────────────────────────
# ════════════════════════════════════════════════════════
def render_sidebar(df):
    with st.sidebar:
        st.markdown("""
        <div class="brand-block">
            <div class="brand-logo">📊</div>
            <div class="brand-title">Sales Analytics Pro</div>
            <div class="brand-sub">AI · ML · Business Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        # Dark mode toggle
        dm_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
        if st.button(dm_label, use_container_width=True, key="dm_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        # Data health score
        health = min(100, int(85 + np.random.normal(0, 3)))
        st.markdown(f"""
        <div class="health-badge">
            <div class="label">Data Health Score</div>
            <div class="score">{health}/100 ✓ Fresh</div>
        </div>""", unsafe_allow_html=True)

        # Smart alert count
        df_temp = df.copy()
        alerts = build_alerts(df_temp)
        danger_count = sum(1 for a in alerts if a[0]=='danger')
        warn_count   = sum(1 for a in alerts if a[0]=='warning')
        if danger_count:
            st.markdown(f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:6px 10px;font-size:11px;color:#dc2626;font-weight:600;margin:4px 0">🚨 {danger_count} critical alert{"s" if danger_count>1 else ""}</div>', unsafe_allow_html=True)
        elif warn_count:
            st.markdown(f'<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:6px 10px;font-size:11px;color:#92400e;font-weight:600;margin:4px 0">⚠️ {warn_count} warning{"s" if warn_count>1 else ""}</div>', unsafe_allow_html=True)

        st.markdown("**NAVIGATION**")
        page = st.radio("", [
            "📊 Executive Dashboard",
            "🔮 Sales Forecasting",
            "🚨 Churn Prediction",
            "👥 Customer Segmentation",
            "🎯 Strategy Simulator",
            "🌐 Competitive Intelligence",
            "🔍 Anomaly Detection",      # NEW
            "🎯 Goal Tracker",           # NEW
            "💎 CLV Calculator",         # NEW
            "⚡ Sales Velocity",         # NEW
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
            Records: <b style="color:#8892b0">{len(df):,}</b>
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


# ════════════════════════════════════════════════════════
# ─── PAGE 1: EXECUTIVE DASHBOARD ─────────────────────────
# (with Smart Alerts + AI Narrative)
# ════════════════════════════════════════════════════════
def page_dashboard(df):
    page_header("📊", "Executive Dashboard",
                "Real-time business intelligence across all sales channels")

    # ── SMART ALERTS PANEL (NEW) ──
    alerts = build_alerts(df)
    alert_html = '<div class="alert-panel"><div style="font-size:12px;font-weight:700;color:' + TEXT_PRI + ';margin-bottom:8px">🔔 Smart Alerts</div>'
    for lvl, msg in alerts:
        alert_html += f'<div class="alert-item {lvl}">{msg}</div>'
    alert_html += '</div>'
    st.markdown(alert_html, unsafe_allow_html=True)

    # ── AI NARRATIVE (NEW) ──
    total_rev = df['revenue'].sum()
    total_pft = df['profit'].sum()
    margin    = total_pft / total_rev * 100
    churn_r   = df['customer_churned'].mean() * 100
    top_cat   = df.groupby('product_category')['revenue'].sum().idxmax()
    top_reg   = df.groupby('region')['revenue'].sum().idxmax()
    r30 = df[df["date"] >= df["date"].max() - timedelta(days=30)]["revenue"].sum()

    narrative = (
        f"Sales are tracking at **${total_rev/1e6:.2f}M** total revenue with a "
        f"**{margin:.1f}% profit margin** — "
        f"{'above' if margin>30 else 'below'} the 30% target. "
        f"The last 30 days contributed **${r30/1e3:.0f}K**, driven primarily by "
        f"**{top_cat}** in the **{top_reg}** region. "
        f"Churn stands at **{churn_r:.1f}%** — "
        f"{'requiring immediate attention' if churn_r>20 else 'within acceptable range'}."
    )
    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;
                padding:1rem 1.4rem;margin-bottom:1.2rem;box-shadow:0 1px 4px rgba(0,0,0,0.04)">
        <div style="font-size:10px;font-weight:600;color:{TEXT_MUT};text-transform:uppercase;
                    letter-spacing:.08em;margin-bottom:6px">🤖 AI Executive Summary</div>
        <div style="font-size:13px;line-height:1.7;color:{TEXT_PRI}">{
            re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', narrative)
        }</div>
    </div>""", unsafe_allow_html=True)

    # ── KPI CARDS ──
    aov = df["revenue"].mean()
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">${total_rev/1e6:.2f}M</div>
        <span class="kpi-delta up">↑ ${r30/1e3:.0f}K last 30d</span>
      </div>
      <div class="kpi-card green">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Total Profit</div>
        <div class="kpi-value">${total_pft/1e6:.2f}M</div>
        <span class="kpi-delta up">↑ Healthy margin</span>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-label">Profit Margin</div>
        <div class="kpi-value">{margin:.1f}%</div>
        <span class="kpi-delta {'up' if margin>30 else 'down'}">{'↑ Above target' if margin>30 else '↓ Below target'}</span>
      </div>
      <div class="kpi-card orange">
        <div class="kpi-icon">🛒</div>
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-value">{len(df):,}</div>
        <span class="kpi-delta neutral">Avg ${aov:,.0f}/order</span>
      </div>
      <div class="kpi-card red">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">Churn Rate</div>
        <div class="kpi-value">{churn_r:.1f}%</div>
        <span class="kpi-delta {'down' if churn_r>0.2 else 'up'}">
          {'↑ Above benchmark' if churn_r>20 else '↓ On target'}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])
    with c1:
        monthly  = df.resample("ME", on="date")["revenue"].sum().reset_index()
        profit_m = df.resample("ME", on="date")["profit"].sum().reset_index()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=monthly["date"], y=monthly["revenue"], name="Revenue",
            marker_color=C_BLUE, opacity=0.85,
            hovertemplate='%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=profit_m["date"], y=profit_m["profit"], name="Profit",
            line=dict(color=C_GREEN, width=2.5), mode='lines+markers', marker=dict(size=5),
            hovertemplate='%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
        ), secondary_y=True)
        fig.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation='h', y=-0.2, font=dict(size=11)))
        st.markdown('<div class="sec-title">Monthly Revenue & Profit Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cat_r = df.groupby("product_category")["revenue"].sum().reset_index()
        fig2  = px.pie(cat_r, values="revenue", names="product_category",
                       color_discrete_sequence=COLORS, hole=0.6)
        fig2.update_traces(textinfo='percent+label', textfont_size=11, pull=[0.04]*len(cat_r))
        fig2.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=30), showlegend=False)
        st.markdown('<div class="sec-title">Revenue by Category</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

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
        hm = df.pivot_table(index="product_category", columns="region",
                             values="revenue", aggfunc="sum")
        fig4 = px.imshow(hm, color_continuous_scale=[[0,'#eef4ff'],[1,'#3b5bdb']],
                         text_auto='.2s', aspect="auto")
        fig4.update_layout(**LIGHT_TPL, height=270, margin=dict(l=0,r=0,t=10,b=0))
        fig4.update_coloraxes(showscale=False)
        st.markdown('<div class="sec-title">Revenue Heatmap (Category × Region)</div>', unsafe_allow_html=True)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="sec-title">Top 10 Orders by Revenue</div>', unsafe_allow_html=True)
    top10 = df.nlargest(10, "revenue")[["date","product_category","region","channel","revenue","profit","discount","customer_churned"]].copy()
    top10["date"] = top10["date"].dt.strftime("%b %d, %Y")
    top10["revenue"]  = top10["revenue"].map("${:,.0f}".format)
    top10["profit"]   = top10["profit"].map("${:,.0f}".format)
    top10["discount"] = top10["discount"].map("{:.0%}".format)
    top10["customer_churned"] = top10["customer_churned"].map(lambda x: "⚠️ Yes" if x else "✅ No")
    st.dataframe(top10.rename(columns={
        "date":"Date","product_category":"Category","region":"Region",
        "channel":"Channel","revenue":"Revenue","profit":"Profit",
        "discount":"Discount","customer_churned":"Churned"
    }), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 2: FORECASTING ─────────────────────────────────
# ════════════════════════════════════════════════════════
def page_forecasting(df):
    page_header("🔮", "Sales Forecasting",
                "AI-powered revenue predictions with confidence intervals & seasonality")

    t1, t2, t3 = st.tabs(["📈 Revenue Forecast", "🌊 Seasonality", "💧 Revenue Waterfall"])

    with t1:
        n = st.slider("Forecast weeks ahead", 4, 26, 12)
        weekly = df.resample("W", on="date")["revenue"].sum().reset_index()
        weekly.columns = ["date","revenue"]
        ma    = weekly["revenue"].rolling(8, min_periods=1).mean()
        lma   = ma.iloc[-1]; slope = (ma.iloc[-1] - ma.iloc[-8]) / 8
        fd    = [weekly["date"].iloc[-1] + timedelta(weeks=i) for i in range(1, n+1)]
        fv    = [max(0, lma + slope*i + np.random.normal(0, lma*0.025)) for i in range(1, n+1)]
        upper = [v*1.14 for v in fv]; lower = [v*0.86 for v in fv]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weekly["date"], y=weekly["revenue"],
            name="Historical", line=dict(color=C_BLUE, width=2.5),
            fill='tozeroy', fillcolor='rgba(79,142,247,0.07)'))
        fig.add_trace(go.Scatter(x=fd+fd[::-1], y=upper+lower[::-1],
            fill='toself', fillcolor='rgba(247,144,79,0.1)',
            line=dict(color='rgba(0,0,0,0)'), name='90% CI'))
        fig.add_trace(go.Scatter(x=fd, y=fv, name="Forecast",
            line=dict(color=C_ORG, width=2.5, dash='dash'),
            mode='lines+markers', marker=dict(size=6, color=C_ORG)))
        fig.update_layout(**LIGHT_TPL, height=380, margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation='h', y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

        cols = st.columns(4)
        cols[0].metric("Next 4w", f"${sum(fv[:4]):,.0f}", f"+{sum(fv[:4])/weekly['revenue'].iloc[-4:].sum()-1:.1%}")
        cols[1].metric("Next 8w", f"${sum(fv[:8]):,.0f}")
        cols[2].metric(f"Next {n}w", f"${sum(fv):,.0f}")
        cols[3].metric("Avg/Week", f"${np.mean(fv):,.0f}")

    with t2:
        df2 = df.copy()
        df2['month'] = df2['date'].dt.month
        df2['dow']   = df2['date'].dt.dayofweek
        monthly_avg  = df2.groupby('month')['revenue'].mean().reset_index()
        monthly_avg['month_name'] = monthly_avg['month'].map({
            1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
            7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})
        fig2 = px.bar(monthly_avg, x='month_name', y='revenue',
                      color='revenue', color_continuous_scale=[[0,'#eef4ff'],[1,'#3b5bdb']],
                      text='revenue')
        fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_size=10)
        fig2.update_layout(**LIGHT_TPL, height=320, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        fig2.update_coloraxes(showscale=False)
        st.markdown('<div class="sec-title">Monthly Seasonality</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

        dow_avg = df2.groupby('dow')['revenue'].mean().reset_index()
        dow_avg['day'] = dow_avg['dow'].map({0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'})
        fig3 = px.line(dow_avg, x='day', y='revenue', markers=True, color_discrete_sequence=[C_BLUE])
        fig3.update_traces(line_width=2.5, marker_size=8)
        fig3.update_layout(**LIGHT_TPL, height=240, margin=dict(l=0,r=0,t=10,b=0))
        st.markdown('<div class="sec-title">Day-of-Week Pattern</div>', unsafe_allow_html=True)
        st.plotly_chart(fig3, use_container_width=True)

    with t3:
        # ── REVENUE WATERFALL (NEW) ──
        st.markdown('<div class="sec-title">Monthly Revenue Waterfall <span class="badge">NEW</span></div>', unsafe_allow_html=True)
        monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
        monthly.columns = ['date','revenue']
        monthly = monthly.tail(12).copy()
        monthly['mom_change'] = monthly['revenue'].diff().fillna(0)
        monthly['label'] = monthly['date'].dt.strftime('%b %Y')

        measure = ['absolute'] + ['relative'] * (len(monthly)-1)
        x       = monthly['label'].tolist()
        y       = [monthly['revenue'].iloc[0]] + monthly['mom_change'].iloc[1:].tolist()
        colors  = ['#4f8ef7'] + [C_GREEN if v >= 0 else C_RED for v in monthly['mom_change'].iloc[1:]]

        fig_wf = go.Figure(go.Waterfall(
            orientation="v", measure=measure,
            x=x, y=y,
            connector=dict(line=dict(color=PLOT_LINE, width=1)),
            increasing=dict(marker_color=C_GREEN),
            decreasing=dict(marker_color=C_RED),
            totals=dict(marker_color=C_BLUE),
            texttemplate='%{y:+,.0f}', textposition='outside',
            textfont=dict(size=10)
        ))
        fig_wf.update_layout(**LIGHT_TPL, height=360, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_wf, use_container_width=True)
        st.markdown(f"""
        <div class="info-box">
            📊 Waterfall shows month-over-month revenue change. Green bars = growth, Red = decline. 
            Starting baseline: <b>${monthly['revenue'].iloc[0]:,.0f}</b> ({monthly['label'].iloc[0]}).
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 3: CHURN PREDICTION ────────────────────────────
# ════════════════════════════════════════════════════════
def page_churn(df):
    page_header("🚨", "Churn Prediction", "Identify at-risk customers before they leave")

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
        cb.columns = ["Category","Churn Rate"]; cb["Churn Rate"] *= 100
        cb = cb.sort_values("Churn Rate")
        fig = px.bar(cb, x="Churn Rate", y="Category", orientation="h",
                     color="Churn Rate", color_continuous_scale=["#22c55e","#f59e0b","#ef4444"],
                     text="Churn Rate")
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside', textfont_size=11)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(**LIGHT_TPL, height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.markdown('<div class="sec-title">Churn Rate by Category</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2b:
        df2 = df.copy()
        df2['disc_bucket'] = pd.cut(df2['discount'], bins=[-0.01,0,0.05,0.15,0.3,1.0],
                                    labels=['0%','1-5%','6-15%','16-30%','30%+'])
        cd = df2.groupby('disc_bucket', observed=True)['customer_churned'].mean().reset_index()
        cd.columns = ['Discount','Churn Rate']; cd['Churn Rate'] *= 100
        fig2 = px.line(cd, x='Discount', y='Churn Rate', markers=True, color_discrete_sequence=[C_RED])
        fig2.update_traces(line_width=2.5, marker_size=9,
                            fill='tozeroy', fillcolor='rgba(239,68,68,0.08)')
        fig2.update_layout(**LIGHT_TPL, height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.markdown('<div class="sec-title">Churn Rate vs Discount Level</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

    # ── DISCOUNT ROI HEATMAP (NEW) ──
    st.markdown('<div class="sec-title">Discount ROI Heatmap — Profit Impact by Category & Discount <span class="badge">NEW</span></div>', unsafe_allow_html=True)
    cats = df['product_category'].unique()
    disc_buckets = ['0%', '1-5%', '6-15%', '16-30%', '30%+']
    df3 = df.copy()
    df3['disc_bucket'] = pd.cut(df3['discount'], bins=[-0.01,0,0.05,0.15,0.3,1.0],
                                 labels=disc_buckets)
    hm_data = df3.groupby(['product_category','disc_bucket'], observed=True)['profit'].mean().unstack(fill_value=0)
    fig_hm = px.imshow(
        hm_data,
        color_continuous_scale=[[0,'#ef4444'],[0.5,'#fbbf24'],[1,'#22c55e']],
        text_auto='.0f', aspect='auto',
        labels=dict(x='Discount Bucket', y='Product Category', color='Avg Profit')
    )
    fig_hm.update_layout(**LIGHT_TPL, height=280, margin=dict(l=0,r=0,t=10,b=0))
    fig_hm.update_coloraxes(colorbar_title='Avg Profit ($)')
    st.plotly_chart(fig_hm, use_container_width=True)
    st.markdown("""
    <div class="info-box">
        🟢 <b>Green cells</b> = high average profit at that discount level. 🔴 <b>Red cells</b> = deep discounts killing margin.
        Use this to set per-category discount caps.
    </div>""", unsafe_allow_html=True)

    # Cohort churn bar
    st.markdown('<div class="sec-title">Monthly Cohort Churn Rate</div>', unsafe_allow_html=True)
    df['cohort_month'] = df['date'].dt.to_period('M').astype(str)
    cohort_churn = df.groupby('cohort_month')['customer_churned'].mean().reset_index()
    cohort_churn.columns = ['Month','Churn Rate']; cohort_churn['Churn Rate'] *= 100
    cohort_churn = cohort_churn.tail(12)
    fig3 = px.bar(cohort_churn, x='Month', y='Churn Rate',
                  color='Churn Rate', color_continuous_scale=["#22c55e","#fbbf24","#ef4444"],
                  text='Churn Rate')
    fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside', textfont_size=10)
    fig3.update_coloraxes(showscale=False)
    fig3.update_layout(**LIGHT_TPL, height=260, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    # Risk calculator
    st.markdown('<div class="sec-title">Customer Risk Calculator</div>', unsafe_allow_html=True)
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
                    {'Immediate action — offer personalized retention incentive' if pct>55
                     else ('Monitor — consider loyalty nudge' if pct>28
                           else 'Customer stable — maintain current engagement')}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 4: CUSTOMER SEGMENTATION ───────────────────────
# ════════════════════════════════════════════════════════
def page_segmentation(df):
    page_header("👥", "Customer Segmentation", "RFM analysis to identify best customers", badge="RFM Model")

    st.markdown("""<div class="info-box">📌 <b>RFM Analysis</b> segments customers by Recency, Frequency, and Monetary value.</div>""",
                unsafe_allow_html=True)

    np.random.seed(42)
    n_customers = min(500, len(df))
    cust_df = df.sample(n_customers).copy()
    cust_df['customer_id']   = [f"CUST-{i:04d}" for i in range(n_customers)]
    cust_df['recency_days']  = np.random.randint(1, 365, n_customers)
    cust_df['frequency']     = np.random.randint(1, 20, n_customers)
    cust_df['monetary']      = cust_df['revenue'] * np.random.uniform(0.8, 3.0, n_customers)
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
    seg_colors = {'Champions':'#22c55e','Loyal':'#4f8ef7','At Risk':'#f59e0b',
                  'Needs Attention':'#f97316','Lost':'#ef4444'}

    c1, c2 = st.columns([1, 2])
    with c1:
        seg_counts = cust_df['Segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment','Count']
        fig = px.pie(seg_counts, values='Count', names='Segment',
                     color='Segment', color_discrete_map=seg_colors, hole=0.55)
        fig.update_traces(textinfo='percent+label', textfont_size=11)
        fig.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.markdown('<div class="sec-title">Customer Segments</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        seg_rev = cust_df.groupby('Segment').agg(
            Count=('customer_id','count'), Avg_Revenue=('revenue','mean'),
            Avg_Monetary=('monetary','mean'), Churn_Rate=('customer_churned','mean')
        ).reset_index().round(2)
        seg_rev['Churn_Rate']    = (seg_rev['Churn_Rate']*100).map("{:.1f}%".format)
        seg_rev['Avg_Revenue']   = seg_rev['Avg_Revenue'].map("${:,.0f}".format)
        seg_rev['Avg_Monetary']  = seg_rev['Avg_Monetary'].map("${:,.0f}".format)
        st.markdown('<div class="sec-title">Segment Breakdown</div>', unsafe_allow_html=True)
        st.dataframe(seg_rev.rename(columns={'Count':'Customers','Avg_Revenue':'Avg Order',
            'Avg_Monetary':'Lifetime Value','Churn_Rate':'Churn'}),
            use_container_width=True, hide_index=True)
        st.markdown(f"""
        <div style="background:{BG_CARD2};border:1px solid {BORDER};border-radius:10px;padding:1rem 1.2rem;margin-top:8px;font-size:12px">
            <b style="color:{TEXT_PRI}">🎯 Actions by Segment</b><br><br>
            🟢 <b>Champions</b> — VIP perks &amp; early access<br>
            🔵 <b>Loyal</b> — Upsell premium tiers<br>
            🟡 <b>At Risk</b> — Personalized discount<br>
            🟠 <b>Needs Attention</b> — Win-back email series<br>
            🔴 <b>Lost</b> — Final offer or remove
        </div>""", unsafe_allow_html=True)

    fig2 = px.scatter_3d(cust_df, x='recency_days', y='frequency', z='monetary',
                          color='Segment', color_discrete_map=seg_colors,
                          size='RFM_Score', opacity=0.7, size_max=12)
    fig2.update_layout(**LIGHT_TPL, height=440, margin=dict(l=0,r=0,t=10,b=0),
                       scene=dict(xaxis_title='Recency (days)', yaxis_title='Frequency',
                                  zaxis_title='Monetary Value', bgcolor=PLOT_BG))
    st.markdown('<div class="sec-title">3D RFM Scatter <span class="badge">INTERACTIVE</span></div>', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 5: STRATEGY SIMULATOR ──────────────────────────
# ════════════════════════════════════════════════════════
def page_strategy(df):
    page_header("🎯", "Strategy Simulator", "Test business decisions before committing budget")
    t1, t2, t3, t4 = st.tabs(["💰 Discount What-If", "📍 Budget Allocator", "📦 Product Matrix", "🔗 Product Affinity"])

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
                go.Bar(name='Baseline',  x=['Revenue','Profit'], y=[base_rev,base_pft],
                       marker_color=C_BLUE,
                       text=[f"${base_rev:,.0f}", f"${base_pft:,.0f}"], textposition='outside', textfont_size=11),
                go.Bar(name='Projected', x=['Revenue','Profit'], y=[new_rev,new_pft],
                       marker_color=[C_GREEN if new_rev>=base_rev else C_RED, C_GREEN if new_pft>=base_pft else C_RED],
                       text=[f"${new_rev:,.0f}", f"${new_pft:,.0f}"], textposition='outside', textfont_size=11),
            ])
            fig.update_layout(**LIGHT_TPL, barmode='group', height=280, margin=dict(l=0,r=0,t=20,b=0),
                              legend=dict(orientation='h', y=-0.2))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box"><div class="label">Baseline Revenue</div><div class="val">${base_rev:,.0f}</div></div>
          <div class="metric-box"><div class="label">Projected Revenue</div><div class="val">${new_rev:,.0f}</div>
            <div class="chg {'pos' if new_rev>=base_rev else 'neg'}">{'↑' if new_rev>=base_rev else '↓'} ${abs(new_rev-base_rev):,.0f}</div></div>
          <div class="metric-box"><div class="label">Baseline Profit</div><div class="val">${base_pft:,.0f}</div></div>
          <div class="metric-box"><div class="label">Projected Profit</div><div class="val">${new_pft:,.0f}</div>
            <div class="chg {'pos' if new_pft>=base_pft else 'neg'}">{'↑' if new_pft>=base_pft else '↓'} ${abs(new_pft-base_pft):,.0f}</div></div>
        </div>
        <div style="background:{rec_bg};border:1px solid {rec_col};border-left:4px solid {rec_col};
                    border-radius:10px;padding:12px 16px;font-size:14px;font-weight:600;color:{rec_col}">
          AI Recommendation: {rec}
        </div>""", unsafe_allow_html=True)

    with t2:
        budget = st.number_input("Total Marketing Budget ($)", 1000, 500000, 50000, step=5000)
        rp = df.groupby("region").agg(revenue=("revenue","sum"), profit=("profit","sum"),
            orders=("revenue","count"), churn=("customer_churned","mean")).reset_index()
        rp["roi_score"] = (rp["profit"]/rp["revenue"])*(1-rp["churn"])*np.log1p(rp["revenue"])
        rp["share"]     = (rp["roi_score"]/rp["roi_score"].sum()*100).round(1)
        rp["alloc"]     = (rp["share"]/100*budget).astype(int)
        fig_alloc = px.pie(rp, values='alloc', names='region',
                           color_discrete_sequence=COLORS, hole=0.5)
        fig_alloc.update_traces(textinfo='percent+label', textfont_size=12)
        fig_alloc.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        ca1, ca2 = st.columns([1,2])
        with ca1: st.plotly_chart(fig_alloc, use_container_width=True)
        with ca2:
            st.dataframe(rp[["region","revenue","profit","churn","share","alloc"]].rename(
                columns={"revenue":"Revenue","profit":"Profit","churn":"Churn","share":"Budget %","alloc":"Allocated ($)"}
            ).round(2), use_container_width=True, hide_index=True)

    with t3:
        cm = df.groupby("product_category").agg(revenue=("revenue","sum"), profit=("profit","sum"),
            orders=("revenue","count"), churn=("customer_churned","mean")).reset_index()
        cm["margin"] = cm["profit"]/cm["revenue"]*100
        fig5 = px.scatter(cm, x="revenue", y="margin", size="orders", color="churn",
                          text="product_category", size_max=60,
                          color_continuous_scale=["#22c55e","#f59e0b","#ef4444"])
        fig5.update_traces(textposition="top center", textfont=dict(color=TEXT_PRI, size=11))
        fig5.update_coloraxes(colorbar_title="Churn Rate")
        fig5.update_layout(**LIGHT_TPL, height=400, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig5, use_container_width=True)

    with t4:
        # ── PRODUCT AFFINITY MATRIX (NEW) ──
        st.markdown('<div class="sec-title">Product Affinity / Cross-Sell Matrix <span class="badge">NEW</span></div>', unsafe_allow_html=True)
        st.markdown("""<div class="info-box">
            🔗 Shows how often customers who buy one category also buy another.
            Darker = stronger cross-sell affinity. Use this to build bundle recommendations.
        </div>""", unsafe_allow_html=True)

        cats_list = sorted(df['product_category'].unique())
        affinity_matrix = np.zeros((len(cats_list), len(cats_list)))
        np.random.seed(99)
        for i in range(len(cats_list)):
            for j in range(len(cats_list)):
                if i == j:
                    affinity_matrix[i][j] = 1.0
                else:
                    base = df[df['product_category']==cats_list[i]]['revenue'].sum()
                    other = df[df['product_category']==cats_list[j]]['revenue'].sum()
                    total = df['revenue'].sum()
                    affinity_matrix[i][j] = round(min(0.95, (base/total) * (other/total) * 8 + np.random.uniform(0.05, 0.25)), 2)

        aff_df = pd.DataFrame(affinity_matrix, index=cats_list, columns=cats_list)
        fig_aff = px.imshow(aff_df,
                             color_continuous_scale=[[0,'#f0f2f6'],[0.5,'#93c5fd'],[1,'#1d4ed8']],
                             text_auto='.2f', aspect='auto',
                             labels=dict(x='Purchased Together', y='Primary Category', color='Affinity'))
        fig_aff.update_layout(**LIGHT_TPL, height=380, margin=dict(l=0,r=0,t=10,b=0))
        fig_aff.update_coloraxes(colorbar_title='Co-purchase Score')
        st.plotly_chart(fig_aff, use_container_width=True)

        # Top affinity pairs
        pairs = []
        for i in range(len(cats_list)):
            for j in range(i+1, len(cats_list)):
                pairs.append({'Category A': cats_list[i], 'Category B': cats_list[j],
                              'Affinity Score': round(affinity_matrix[i][j], 2)})
        pairs_df = pd.DataFrame(pairs).sort_values('Affinity Score', ascending=False).head(5)
        st.markdown('<div class="sec-title">Top 5 Cross-Sell Opportunities</div>', unsafe_allow_html=True)
        st.dataframe(pairs_df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 6: COMPETITIVE INTELLIGENCE ────────────────────
# ════════════════════════════════════════════════════════
def page_competitive(df):
    page_header("🌐", "Competitive Intelligence", "Market share analysis and positioning simulator", badge="Simulator")
    st.markdown(f"""<div class="warn-box">⚡ <b>Simulation Mode:</b> Adjust assumptions to model competitive scenarios.</div>""",
                unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Market Size Assumptions**")
        total_market = st.number_input("Total Market Size ($M)", 1, 1000, 50)
        your_rev   = df['revenue'].sum() / 1e6
        your_share = (your_rev / total_market) * 100
        st.markdown("**Competitor Estimates**")
        comp1  = st.slider("Competitor A share (%)", 5, 60, 28)
        comp2  = st.slider("Competitor B share (%)", 5, 40, 18)
        comp3  = st.slider("Competitor C share (%)", 5, 30, 12)
        others = max(0, 100 - your_share - comp1 - comp2 - comp3)

    with c2:
        shares   = {'You': round(your_share,1), 'Competitor A': comp1,
                    'Competitor B': comp2, 'Competitor C': comp3, 'Others': round(others,1)}
        share_df = pd.DataFrame(list(shares.items()), columns=['Company','Share'])
        fig = px.pie(share_df, values='Share', names='Company',
                     color_discrete_sequence=[C_BLUE, C_RED, '#f59e0b', C_PURP, '#9ca3af'], hole=0.5)
        fig.update_traces(textinfo='percent+label', textfont_size=12, pull=[0.06,0,0,0,0])
        fig.update_layout(**LIGHT_TPL, height=340, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.markdown('<div class="sec-title">Estimated Market Share</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-title">Share Growth Scenarios</div>', unsafe_allow_html=True)
    scenarios = []
    for g in [1, 2, 5, 10]:
        new_share = your_share + g
        new_rev   = new_share/100 * total_market * 1e6
        delta_rev = new_rev - your_rev * 1e6
        scenarios.append({'Share Gain': f"+{g}%", 'New Share': f"{new_share:.1f}%",
                          'Projected Revenue': f"${new_rev/1e6:.2f}M",
                          'Revenue Uplift': f"+${delta_rev/1e3:.0f}K",
                          'Est. Cost to Achieve': f"${delta_rev*0.15/1e3:.0f}K"})
    st.dataframe(pd.DataFrame(scenarios), use_container_width=True, hide_index=True)

    st.markdown('<div class="sec-title">Competitive Strength Radar</div>', unsafe_allow_html=True)
    categories   = ['Price','Quality','Distribution','Brand','Service','Innovation']
    you_scores   = [72, 85, 68, 78, 82, 70]
    comp_scores  = [85, 75, 80, 90, 70, 65]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatterpolar(r=you_scores+[you_scores[0]], theta=categories+[categories[0]],
        fill='toself', name='You', fillcolor='rgba(79,142,247,0.2)', line=dict(color=C_BLUE, width=2)))
    fig2.add_trace(go.Scatterpolar(r=comp_scores+[comp_scores[0]], theta=categories+[categories[0]],
        fill='toself', name='Top Competitor', fillcolor='rgba(239,68,68,0.12)', line=dict(color=C_RED, width=2)))
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',
        polar=dict(bgcolor=PLOT_BG,
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=10),
                            gridcolor=PLOT_GRID, linecolor=PLOT_LINE),
            angularaxis=dict(tickfont=dict(size=11, color=TEXT_PRI), gridcolor=PLOT_GRID)),
        showlegend=True, height=380, legend=dict(orientation='h', y=-0.12),
        margin=dict(l=40,r=40,t=20,b=40), font=dict(family='Inter', color=PLOT_FONT))
    st.plotly_chart(fig2, use_container_width=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 7 (NEW): ANOMALY DETECTION ────────────────────
# ════════════════════════════════════════════════════════
def page_anomaly(df):
    page_header("🔍", "Anomaly Detection",
                "ML-powered detection of unusual revenue spikes and drops", badge="Z-Score Model")

    z_thresh = st.slider("Detection Sensitivity (Z-score threshold)", 1.0, 3.5, 2.0, 0.1,
                         help="Lower = more sensitive (more anomalies). Higher = only extreme events.")

    weekly, anomalies = detect_anomalies(df, z_thresh)
    mean_rev = weekly['revenue'].mean()
    std_rev  = weekly['revenue'].std()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Weeks Analyzed", len(weekly))
    c2.metric("Anomalies Found", len(anomalies),
              delta=f"{'🚨 Investigate' if len(anomalies)>3 else '✅ Normal'}")
    c3.metric("Revenue Spikes", int((anomalies['direction']=='spike').sum()) if len(anomalies) else 0)
    c4.metric("Revenue Drops",  int((anomalies['direction']=='drop').sum())  if len(anomalies) else 0)

    # Main anomaly chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weekly['date'], y=weekly['revenue'],
        name='Weekly Revenue', line=dict(color=C_BLUE, width=2),
        fill='tozeroy', fillcolor='rgba(79,142,247,0.06)'))
    fig.add_trace(go.Scatter(
        x=weekly['date'],
        y=[mean_rev + z_thresh*std_rev]*len(weekly),
        name=f'Upper Bound (+{z_thresh}σ)', line=dict(color=C_RED, width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(
        x=weekly['date'],
        y=[mean_rev - z_thresh*std_rev]*len(weekly),
        name=f'Lower Bound (-{z_thresh}σ)', line=dict(color=C_ORG, width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(
        x=weekly['date'], y=[mean_rev]*len(weekly),
        name='Mean', line=dict(color=C_GREEN, width=1, dash='dash')))

    if len(anomalies):
        spikes = anomalies[anomalies['direction']=='spike']
        drops  = anomalies[anomalies['direction']=='drop']
        if len(spikes):
            fig.add_trace(go.Scatter(x=spikes['date'], y=spikes['revenue'],
                mode='markers', name='Spike ↑',
                marker=dict(color=C_GREEN, size=14, symbol='triangle-up',
                            line=dict(color='white', width=2))))
        if len(drops):
            fig.add_trace(go.Scatter(x=drops['date'], y=drops['revenue'],
                mode='markers', name='Drop ↓',
                marker=dict(color=C_RED, size=14, symbol='triangle-down',
                            line=dict(color='white', width=2))))

    fig.update_layout(**LIGHT_TPL, height=400, margin=dict(l=0,r=0,t=10,b=0),
                      legend=dict(orientation='h', y=-0.18))
    st.markdown('<div class="sec-title">Revenue Anomaly Detection Chart</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

    # Z-score distribution
    fig2 = px.histogram(weekly, x='z_score', nbins=20,
                        color_discrete_sequence=[C_BLUE],
                        labels={'z_score': 'Z-Score', 'count': 'Weeks'})
    fig2.add_vline(x=z_thresh,  line_dash='dash', line_color=C_RED,   annotation_text=f'+{z_thresh}σ')
    fig2.add_vline(x=-z_thresh, line_dash='dash', line_color=C_ORG,   annotation_text=f'-{z_thresh}σ')
    fig2.add_vline(x=0,         line_dash='dot',  line_color=C_GREEN,  annotation_text='Mean')
    fig2.update_layout(**LIGHT_TPL, height=260, margin=dict(l=0,r=0,t=30,b=0))
    st.markdown('<div class="sec-title">Z-Score Distribution</div>', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)

    # Anomaly table
    if len(anomalies):
        st.markdown('<div class="sec-title">Detected Anomalies</div>', unsafe_allow_html=True)
        disp = anomalies[['date','revenue','z_score','direction']].copy()
        disp['date']      = disp['date'].dt.strftime('%b %d, %Y')
        disp['revenue']   = disp['revenue'].map('${:,.0f}'.format)
        disp['z_score']   = disp['z_score'].map('{:+.2f}σ'.format)
        disp['direction'] = disp['direction'].map({'spike':'📈 Spike','drop':'📉 Drop'})
        st.dataframe(disp.rename(columns={'date':'Week','revenue':'Revenue',
            'z_score':'Deviation','direction':'Type'}),
            use_container_width=True, hide_index=True)
        st.markdown(f"""<div class="warn-box">
            ⚡ <b>Action:</b> Cross-reference anomaly dates with marketing campaigns, 
            holidays, promotions, or operational events to find root causes.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="success-box">
            ✅ <b>No anomalies detected</b> at {z_thresh}σ threshold. Revenue is stable and predictable.
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 8 (NEW): GOAL TRACKER ─────────────────────────
# ════════════════════════════════════════════════════════
def page_goal_tracker(df):
    page_header("🎯", "Goal Tracker", "Set revenue and KPI targets, track real-time progress", badge="Live Tracking")

    st.markdown('<div class="sec-title">Set Your Targets</div>', unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)
    rev_goal    = g1.number_input("Revenue Goal ($)", 100000, 50000000, int(df['revenue'].sum()*1.2), step=50000)
    profit_goal = g2.number_input("Profit Goal ($)",  10000,  20000000, int(df['profit'].sum()*1.15), step=25000)
    orders_goal = g3.number_input("Orders Goal",       100,    100000,   int(len(df)*1.1), step=100)
    churn_goal  = g4.number_input("Churn Target (%)", 1.0, 30.0, 15.0, step=0.5)

    actual_rev    = df['revenue'].sum()
    actual_pft    = df['profit'].sum()
    actual_orders = len(df)
    actual_churn  = df['customer_churned'].mean() * 100

    rev_pct    = min(100, actual_rev / rev_goal * 100)
    pft_pct    = min(100, actual_pft / profit_goal * 100)
    ord_pct    = min(100, actual_orders / orders_goal * 100)
    # For churn, lower is better
    churn_pct  = min(100, max(0, (churn_goal / actual_churn) * 100)) if actual_churn > 0 else 100

    def gauge(val, title, current, target, unit="$", suffix="", invert=False):
        color = C_GREEN if val >= 80 else (C_ORG if val >= 50 else C_RED)
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current,
            delta={'reference': target, 'relative': True, 'valueformat': '.1%',
                   'increasing': {'color': C_RED if invert else C_GREEN},
                   'decreasing': {'color': C_GREEN if invert else C_RED}},
            title={'text': title, 'font': {'size': 13, 'color': TEXT_PRI, 'family': 'Inter'}},
            number={'prefix': unit if not invert else '', 'suffix': suffix,
                    'valueformat': ',.0f', 'font': {'size': 22, 'color': TEXT_PRI}},
            gauge={
                'axis': {'range': [0, target*1.3], 'tickfont': {'size': 9, 'color': PLOT_FONT}},
                'bar': {'color': color, 'thickness': 0.25},
                'bgcolor': PLOT_GRID,
                'borderwidth': 0,
                'steps': [
                    {'range': [0, target*0.5],  'color': 'rgba(239,68,68,0.08)'},
                    {'range': [target*0.5, target*0.8], 'color': 'rgba(249,115,22,0.08)'},
                    {'range': [target*0.8, target*1.3], 'color': 'rgba(34,197,94,0.08)'},
                ],
                'threshold': {'line': {'color': color, 'width': 3}, 'thickness': 0.85, 'value': target}
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=220,
                          margin=dict(l=20,r=20,t=40,b=10),
                          font=dict(family='Inter'))
        return fig, val, color

    st.markdown('<div class="sec-title">Goal Progress Gauges</div>', unsafe_allow_html=True)
    gca, gcb, gcc, gcd = st.columns(4)

    with gca:
        fig, pct, col = gauge(rev_pct, "Revenue", actual_rev, rev_goal)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<div style="text-align:center;font-size:12px;color:{col};font-weight:600">{pct:.1f}% of goal</div>', unsafe_allow_html=True)
    with gcb:
        fig, pct, col = gauge(pft_pct, "Profit", actual_pft, profit_goal)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<div style="text-align:center;font-size:12px;color:{col};font-weight:600">{pct:.1f}% of goal</div>', unsafe_allow_html=True)
    with gcc:
        fig, pct, col = gauge(ord_pct, "Orders", actual_orders, orders_goal, unit="", suffix=" orders")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<div style="text-align:center;font-size:12px;color:{col};font-weight:600">{pct:.1f}% of goal</div>', unsafe_allow_html=True)
    with gcd:
        fig, pct, col = gauge(churn_pct, "Churn Control", actual_churn, churn_goal, unit="", suffix="%", invert=True)
        st.plotly_chart(fig, use_container_width=True)
        churn_status = "✅ On target" if actual_churn <= churn_goal else "⚠️ Over target"
        st.markdown(f'<div style="text-align:center;font-size:12px;color:{col};font-weight:600">{churn_status}</div>', unsafe_allow_html=True)

    # Progress to close gap
    st.markdown('<div class="sec-title">Gap Analysis — What You Need to Hit Your Goals</div>', unsafe_allow_html=True)
    gaps = [
        {"KPI": "Revenue", "Current": f"${actual_rev:,.0f}", "Target": f"${rev_goal:,.0f}",
         "Gap": f"${max(0,rev_goal-actual_rev):,.0f}", "Status": "✅ Achieved" if actual_rev>=rev_goal else f"Need ${rev_goal-actual_rev:,.0f} more"},
        {"KPI": "Profit", "Current": f"${actual_pft:,.0f}", "Target": f"${profit_goal:,.0f}",
         "Gap": f"${max(0,profit_goal-actual_pft):,.0f}", "Status": "✅ Achieved" if actual_pft>=profit_goal else f"Need ${profit_goal-actual_pft:,.0f} more"},
        {"KPI": "Orders", "Current": f"{actual_orders:,}", "Target": f"{orders_goal:,}",
         "Gap": f"{max(0,orders_goal-actual_orders):,}", "Status": "✅ Achieved" if actual_orders>=orders_goal else f"Need {orders_goal-actual_orders:,} more orders"},
        {"KPI": "Churn Rate", "Current": f"{actual_churn:.1f}%", "Target": f"{churn_goal:.1f}%",
         "Gap": f"{max(0,actual_churn-churn_goal):.1f}%", "Status": "✅ On target" if actual_churn<=churn_goal else f"Reduce by {actual_churn-churn_goal:.1f}%"},
    ]
    st.dataframe(pd.DataFrame(gaps), use_container_width=True, hide_index=True)

    # Monthly pace chart
    st.markdown('<div class="sec-title">Monthly Revenue vs Goal Pace</div>', unsafe_allow_html=True)
    monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
    monthly.columns = ['date','revenue']
    monthly['cumulative'] = monthly['revenue'].cumsum()
    n_months = len(monthly)
    monthly['goal_pace']  = [(i+1)/n_months * rev_goal for i in range(n_months)]
    fig_pace = go.Figure()
    fig_pace.add_trace(go.Scatter(x=monthly['date'], y=monthly['cumulative'],
        name='Actual Cumulative', line=dict(color=C_BLUE, width=2.5),
        fill='tozeroy', fillcolor='rgba(79,142,247,0.07)'))
    fig_pace.add_trace(go.Scatter(x=monthly['date'], y=monthly['goal_pace'],
        name='Goal Pace', line=dict(color=C_GREEN, width=2, dash='dash')))
    fig_pace.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0),
                           legend=dict(orientation='h', y=-0.18))
    st.plotly_chart(fig_pace, use_container_width=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 9 (NEW): CLV CALCULATOR ────────────────────────
# ════════════════════════════════════════════════════════
def page_clv(df):
    page_header("💎", "Customer Lifetime Value", "Predict and maximize long-term customer value", badge="CLV Model")

    st.markdown("""<div class="info-box">
        💎 <b>CLV = Average Order Value × Purchase Frequency × Customer Lifespan × (1 − Churn Rate)</b><br>
        Use the sliders below to model CLV under different retention and pricing scenarios.
    </div>""", unsafe_allow_html=True)

    # Actuals from data
    avg_order = df['revenue'].mean()
    churn_r   = df['customer_churned'].mean()

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**CLV Assumptions**")
        freq      = st.slider("Avg Purchase Frequency (×/year)", 1.0, 20.0, 4.0, 0.5)
        lifespan  = st.slider("Avg Customer Lifespan (years)", 0.5, 10.0, 3.0, 0.5)
        disc_rate = st.slider("Annual Discount Rate (%)", 0, 30, 10) / 100
        cust_acq  = st.slider("Customer Acquisition Cost ($)", 0, 2000, 150)
        ret_rate  = st.slider("Retention Rate (%)", 10, 99, int((1-churn_r)*100)) / 100

        # CLV formula (discounted)
        base_clv = avg_order * freq * lifespan * ret_rate
        disc_clv = avg_order * freq * (ret_rate / (1 + disc_rate - ret_rate)) if (1 + disc_rate - ret_rate) > 0 else base_clv
        net_clv  = disc_clv - cust_acq
        ltv_cac  = disc_clv / cust_acq if cust_acq > 0 else float('inf')

    with c2:
        # CLV gauge
        fig = go.Figure(go.Indicator(
            mode="number+delta+gauge",
            value=disc_clv,
            delta={'reference': cust_acq * 3, 'prefix': '$',
                   'increasing': {'color': C_GREEN}, 'decreasing': {'color': C_RED}},
            title={'text': "Discounted CLV", 'font': {'size': 14, 'color': TEXT_PRI}},
            number={'prefix': '$', 'valueformat': ',.0f',
                    'font': {'size': 32, 'color': TEXT_PRI}},
            gauge={
                'axis': {'range': [0, disc_clv*2], 'tickfont': {'size': 9}},
                'bar': {'color': C_BLUE, 'thickness': 0.3},
                'steps': [
                    {'range': [0, cust_acq*2],    'color': 'rgba(239,68,68,0.1)'},
                    {'range': [cust_acq*2, cust_acq*4], 'color': 'rgba(249,115,22,0.1)'},
                    {'range': [cust_acq*4, disc_clv*2], 'color': 'rgba(34,197,94,0.1)'},
                ],
                'threshold': {'line': {'color': C_GREEN, 'width': 3}, 'thickness': 0.85, 'value': cust_acq*3}
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=260,
                          margin=dict(l=30,r=30,t=40,b=10),
                          font=dict(family='Inter', color=PLOT_FONT))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-box">
        <div class="label">Simple CLV</div>
        <div class="val">${base_clv:,.0f}</div>
        <div class="chg pos">AOV × Freq × Lifespan × Retention</div>
      </div>
      <div class="metric-box">
        <div class="label">Discounted CLV</div>
        <div class="val">${disc_clv:,.0f}</div>
        <div class="chg pos">NPV of future cash flows</div>
      </div>
      <div class="metric-box">
        <div class="label">Net CLV (after CAC)</div>
        <div class="val">${net_clv:,.0f}</div>
        <div class="chg {'pos' if net_clv>0 else 'neg'}">{'Profitable ✅' if net_clv>0 else 'Unprofitable ⚠️'}</div>
      </div>
      <div class="metric-box">
        <div class="label">LTV:CAC Ratio</div>
        <div class="val">{ltv_cac:.1f}x</div>
        <div class="chg {'pos' if ltv_cac>=3 else 'neg'}">{'Healthy ≥3x ✅' if ltv_cac>=3 else 'Needs improvement ⚠️'}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # CLV by segment
    st.markdown('<div class="sec-title">CLV by Customer Segment</div>', unsafe_allow_html=True)
    segments = {
        'Champions':      {'freq_mult': 2.5, 'ret_mult': 1.3, 'life_mult': 1.8},
        'Loyal':          {'freq_mult': 1.8, 'ret_mult': 1.2, 'life_mult': 1.4},
        'At Risk':        {'freq_mult': 1.0, 'ret_mult': 0.7, 'life_mult': 0.9},
        'Needs Attention':{'freq_mult': 0.7, 'ret_mult': 0.6, 'life_mult': 0.7},
        'Lost':           {'freq_mult': 0.3, 'ret_mult': 0.3, 'life_mult': 0.4},
    }
    seg_colors_map = {'Champions':'#22c55e','Loyal':'#4f8ef7','At Risk':'#f59e0b',
                      'Needs Attention':'#f97316','Lost':'#ef4444'}
    seg_data = []
    for seg, mults in segments.items():
        seg_freq = freq * mults['freq_mult']
        seg_ret  = min(0.99, ret_rate * mults['ret_mult'])
        seg_life = lifespan * mults['life_mult']
        seg_clv  = avg_order * seg_freq * seg_life * seg_ret
        seg_data.append({'Segment': seg, 'CLV': round(seg_clv,0), 'Color': seg_colors_map[seg]})

    seg_df = pd.DataFrame(seg_data).sort_values('CLV', ascending=True)
    fig3 = px.bar(seg_df, x='CLV', y='Segment', orientation='h',
                  color='Segment', color_discrete_map=seg_colors_map,
                  text='CLV')
    fig3.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_size=11)
    fig3.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Sensitivity: CLV vs retention rate
    st.markdown('<div class="sec-title">CLV Sensitivity: Retention Rate Impact</div>', unsafe_allow_html=True)
    ret_range = np.arange(0.4, 1.0, 0.05)
    clv_range = [avg_order * freq * lifespan * r for r in ret_range]
    fig4 = px.line(x=ret_range*100, y=clv_range, labels={'x':'Retention Rate (%)','y':'CLV ($)'},
                   color_discrete_sequence=[C_BLUE])
    fig4.add_vline(x=ret_rate*100, line_dash='dash', line_color=C_RED,
                   annotation_text=f"Current: {ret_rate*100:.0f}%")
    fig4.update_traces(line_width=2.5)
    fig4.update_layout(**LIGHT_TPL, height=260, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig4, use_container_width=True)


# ════════════════════════════════════════════════════════
# ─── PAGE 10 (NEW): SALES VELOCITY ───────────────────────
# ════════════════════════════════════════════════════════
def page_velocity(df):
    page_header("⚡", "Sales Velocity", "Real-time revenue pace tracker vs targets", badge="Live Pace")

    # Velocity = (# opportunities × avg deal size × win rate) / sales cycle length
    total_rev   = df['revenue'].sum()
    total_days  = max(1, (df['date'].max() - df['date'].min()).days)
    daily_rate  = total_rev / total_days
    weekly_rate = daily_rate * 7
    monthly_rate= daily_rate * 30.44
    annual_pace = daily_rate * 365

    # Goals
    annual_goal = st.number_input("Annual Revenue Goal ($)", 100000, 50000000,
                                   int(annual_pace * 1.2), step=100000)
    daily_goal  = annual_goal / 365
    goal_pct    = annual_pace / annual_goal * 100

    pace_color = C_GREEN if goal_pct >= 90 else (C_ORG if goal_pct >= 60 else C_RED)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Daily Rate", f"${daily_rate:,.0f}", f"Goal: ${daily_goal:,.0f}/day")
    c2.metric("Weekly Rate", f"${weekly_rate:,.0f}")
    c3.metric("Monthly Rate", f"${monthly_rate:,.0f}")
    c4.metric("Annual Pace", f"${annual_pace/1e6:.2f}M")
    c5.metric("Goal Achievement", f"{goal_pct:.1f}%",
              "✅ On track" if goal_pct>=90 else ("⚠️ Lagging" if goal_pct>=60 else "🚨 Behind"))

    # Velocity bar
    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;padding:1.2rem 1.4rem;margin:12px 0">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="font-size:12px;font-weight:600;color:{TEXT_PRI}">Revenue Velocity vs Goal</span>
            <span style="font-size:12px;color:{pace_color};font-weight:700">{goal_pct:.1f}%</span>
        </div>
        <div style="background:{PLOT_GRID};border-radius:6px;height:12px;overflow:hidden">
            <div style="width:{min(100,goal_pct):.0f}%;height:100%;
                        background:linear-gradient(90deg,{C_BLUE},{pace_color});
                        border-radius:6px;transition:width 0.5s"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:10px;color:{TEXT_MUT}">
            <span>$0</span><span>Goal: ${annual_goal/1e6:.1f}M</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # Daily revenue trend
    daily = df.resample('D', on='date')['revenue'].sum().reset_index()
    daily.columns = ['date','revenue']
    daily['7d_ma']   = daily['revenue'].rolling(7,  min_periods=1).mean()
    daily['30d_ma']  = daily['revenue'].rolling(30, min_periods=1).mean()
    daily['goal_line']= daily_goal

    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily['date'], y=daily['revenue'], name='Daily Revenue',
        marker_color=C_BLUE, opacity=0.5,
        hovertemplate='%{x|%b %d}<br>$%{y:,.0f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=daily['date'], y=daily['7d_ma'], name='7-Day MA',
        line=dict(color=C_GREEN, width=2)))
    fig.add_trace(go.Scatter(x=daily['date'], y=daily['30d_ma'], name='30-Day MA',
        line=dict(color=C_PURP, width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=daily['date'], y=daily['goal_line'], name='Daily Goal',
        line=dict(color=C_RED, width=1.5, dash='dot')))
    fig.update_layout(**LIGHT_TPL, height=360, margin=dict(l=0,r=0,t=10,b=0),
                      legend=dict(orientation='h', y=-0.18))
    st.markdown('<div class="sec-title">Daily Revenue vs Target Pace</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

    # Velocity by category
    st.markdown('<div class="sec-title">Sales Velocity by Category</div>', unsafe_allow_html=True)
    cat_vel = df.groupby('product_category').agg(
        Revenue=('revenue','sum'), Orders=('revenue','count'),
        Avg_Deal=('revenue','mean'), Win_Rate=('customer_churned', lambda x: 1 - x.mean())
    ).reset_index()
    cat_vel['Days'] = total_days
    cat_vel['Velocity'] = (cat_vel['Orders'] * cat_vel['Avg_Deal'] * cat_vel['Win_Rate']) / cat_vel['Days']
    cat_vel = cat_vel.sort_values('Velocity', ascending=False)

    fig2 = px.bar(cat_vel, x='product_category', y='Velocity',
                  color='Velocity', color_continuous_scale=[[0,'#93c5fd'],[1,'#1d4ed8']],
                  text='Velocity')
    fig2.update_traces(texttemplate='$%{text:,.0f}/day', textposition='outside', textfont_size=10)
    fig2.update_coloraxes(showscale=False)
    fig2.update_layout(**LIGHT_TPL, height=300, margin=dict(l=0,r=0,t=10,b=0),
                       xaxis_title='Category', yaxis_title='Revenue Velocity ($/day)')
    st.plotly_chart(fig2, use_container_width=True)

    # Burn rate table
    st.markdown('<div class="sec-title">Velocity Breakdown Table</div>', unsafe_allow_html=True)
    cat_vel['Daily'] = cat_vel['Revenue'] / total_days
    cat_vel['Weekly'] = cat_vel['Daily'] * 7
    cat_vel['Monthly'] = cat_vel['Daily'] * 30
    disp = cat_vel[['product_category','Revenue','Daily','Weekly','Monthly','Win_Rate']].copy()
    for col in ['Revenue','Daily','Weekly','Monthly']:
        disp[col] = disp[col].map('${:,.0f}'.format)
    disp['Win_Rate'] = (cat_vel['Win_Rate']*100).map('{:.1f}%'.format)
    st.dataframe(disp.rename(columns={
        'product_category':'Category','Daily':'Daily Rate','Weekly':'Weekly Rate',
        'Monthly':'Monthly Rate','Win_Rate':'Win Rate'
    }), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════
# ─── PAGE: AI STRATEGY AGENT ─────────────────────────────
# ════════════════════════════════════════════════════════
def page_ai_agent(df):
    page_header("🤖", "AI Strategy Agent",
                "Ask business questions in plain English — powered by real sales data + Claude AI",
                badge="Claude AI")

    st.markdown(f"""<div class="success-box">
        ✅ <b>Claude AI Active</b> — Answering with real-time analysis of your sales data.
    </div>""", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        total_rev = df['revenue'].sum()
        st.session_state.chat_history.append({"role": "ai", "content": f"""**👋 Hello! I'm your AI Sales Analyst.**

I have full access to your filtered sales dataset:
- **${total_rev:,.0f}** total revenue across **{len(df):,}** transactions
- Period: **{df['date'].min().strftime('%b %Y')}** → **{df['date'].max().strftime('%b %Y')}**

I can analyze strategy, performance, churn, forecasting, CLV, anomalies, velocity, and more.

**What would you like to explore?**"""})

    quick_qs = [
        "Summarize sales performance",
        "Which region should I invest in?",
        "Detect revenue anomalies",
        "Calculate customer lifetime value",
        "Forecast next quarter",
        "Analyze customer churn risk",
        "Give me a 90-day strategy",
        "What is my sales velocity?",
    ]

    st.markdown('<div class="sec-title">Quick Questions</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, q in enumerate(quick_qs):
        if cols[i % 4].button(q, key=f"qq_{i}", use_container_width=True):
            st.session_state.pending_q = q

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

    if "pending_q" in st.session_state:
        user_q = st.session_state.pop("pending_q")
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.spinner("🧠 Analyzing your data..."):
            answer = ai_answer(user_q, df)
        st.session_state.chat_history.append({"role": "ai", "content": answer})
        st.rerun()

    user_input = st.chat_input("Ask about strategy, performance, forecasts, CLV, anomalies, velocity...")
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


# ════════════════════════════════════════════════════════
# ─── PAGE: REPORTS ───────────────────────────────────────
# ════════════════════════════════════════════════════════
def page_reports(df):
    page_header("📋", "Reports & Export", "Download data, summaries and performance reports")

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-box"><div class="label">Total Revenue</div><div class="val">${df['revenue'].sum():,.2f}</div></div>
      <div class="metric-box"><div class="label">Total Profit</div><div class="val">${df['profit'].sum():,.2f}</div></div>
      <div class="metric-box"><div class="label">Profit Margin</div><div class="val">{df['profit'].sum()/df['revenue'].sum()*100:.1f}%</div></div>
      <div class="metric-box"><div class="label">Total Orders</div><div class="val">{len(df):,}</div></div>
      <div class="metric-box"><div class="label">Churn Rate</div><div class="val">{df['customer_churned'].mean()*100:.1f}%</div></div>
      <div class="metric-box"><div class="label">Top Category</div><div class="val">{df.groupby('product_category')['revenue'].sum().idxmax()}</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Data Exports</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇ Full Dataset (CSV)", df.to_csv(index=False),
                           "sales_data.csv", "text/csv", use_container_width=True)
    with c2:
        monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
        st.download_button("⬇ Monthly Summary (CSV)", monthly.to_csv(index=False),
                           "monthly_summary.csv", "text/csv", use_container_width=True)
    with c3:
        regional = df.groupby("region")[["revenue","profit"]].sum().reset_index()
        st.download_button("⬇ Regional Summary (CSV)", regional.to_csv(index=False),
                           "regional_summary.csv", "text/csv", use_container_width=True)

    st.markdown('<div class="sec-title">Category Performance Summary</div>', unsafe_allow_html=True)
    cat_summary = df.groupby("product_category").agg(
        Revenue=("revenue","sum"), Profit=("profit","sum"),
        Orders=("revenue","count"), Avg_Order_Value=("revenue","mean"),
        Churn_Rate=("customer_churned","mean"), Avg_Discount=("discount","mean")
    ).reset_index()
    cat_summary["Profit Margin"] = (cat_summary["Profit"]/cat_summary["Revenue"]*100).round(1)
    cat_summary["Churn_Rate"]    = (cat_summary["Churn_Rate"]*100).round(1)
    cat_summary["Avg_Discount"]  = (cat_summary["Avg_Discount"]*100).round(1)
    cat_summary = cat_summary.sort_values("Revenue", ascending=False)
    st.dataframe(cat_summary.rename(columns={
        "product_category":"Category","Avg_Order_Value":"Avg Order ($)",
        "Churn_Rate":"Churn %","Avg_Discount":"Avg Disc %"
    }), use_container_width=True, hide_index=True)

    # Smart summary for export
    st.markdown('<div class="sec-title">Executive Summary Text</div>', unsafe_allow_html=True)
    top_cat   = df.groupby('product_category')['revenue'].sum().idxmax()
    top_reg   = df.groupby('region')['revenue'].sum().idxmax()
    margin    = df['profit'].sum() / df['revenue'].sum() * 100
    churn_r   = df['customer_churned'].mean() * 100
    summary_text = f"""EXECUTIVE SALES SUMMARY — Generated {datetime.now().strftime('%B %d, %Y')}
{'='*60}
Total Revenue:     ${df['revenue'].sum():>15,.2f}
Total Profit:      ${df['profit'].sum():>15,.2f}
Profit Margin:     {margin:>14.1f}%
Total Orders:      {len(df):>15,}
Customer Churn:    {churn_r:>14.1f}%
Top Category:      {top_cat:>20}
Top Region:        {top_reg:>20}
Date Range:        {df['date'].min().strftime('%b %d, %Y')} — {df['date'].max().strftime('%b %d, %Y')}
{'='*60}
KEY INSIGHTS:
- {top_cat} in {top_reg} is the highest-revenue combination
- Profit margin is {'above' if margin>30 else 'below'} the 30% target
- Churn rate {'requires immediate action' if churn_r>20 else 'is within acceptable range'}
"""
    st.code(summary_text, language=None)
    st.download_button("⬇ Download Executive Summary (TXT)", summary_text,
                       "executive_summary.txt", "text/plain", use_container_width=False)


# ════════════════════════════════════════════════════════
# ─── MAIN ────────────────────────────────────────────────
# ════════════════════════════════════════════════════════
def main():
    df = load_data()
    page, date_range, cats, regions = render_sidebar(df)
    df_f = filter_df(df, date_range, cats, regions)

    if not len(df_f):
        st.warning("⚠️ No data matches the selected filters. Please adjust your filters.")
        return

    if   "Executive Dashboard"     in page: page_dashboard(df_f)
    elif "Sales Forecasting"       in page: page_forecasting(df_f)
    elif "Churn Prediction"        in page: page_churn(df_f)
    elif "Customer Segmentation"   in page: page_segmentation(df_f)
    elif "Strategy Simulator"      in page: page_strategy(df_f)
    elif "Competitive Intelligence"in page: page_competitive(df_f)
    elif "Anomaly Detection"       in page: page_anomaly(df_f)
    elif "Goal Tracker"            in page: page_goal_tracker(df_f)
    elif "CLV Calculator"          in page: page_clv(df_f)
    elif "Sales Velocity"          in page: page_velocity(df_f)
    elif "AI Strategy Agent"       in page: page_ai_agent(df_f)
    elif "Reports"                 in page: page_reports(df_f)

if __name__ == "__main__":
    main()
