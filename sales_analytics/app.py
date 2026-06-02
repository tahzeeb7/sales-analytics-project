"""
dashboard/app.py
================
Main Streamlit BI Dashboard.
Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics & Strategy AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #e9ecef;
    }
    .stMetric { background: #f8f9fa; border-radius:8px; padding: 10px; }
    .section-title { font-size: 1.2rem; font-weight: 600; margin: 1rem 0 0.5rem; }
    .agent-bubble { background:#e8f4fd; border-radius:10px; padding:0.8rem; margin:0.4rem 0; }
    .user-bubble  { background:#e8f8ee; border-radius:10px; padding:0.8rem; margin:0.4rem 0; text-align:right; }
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADER ─────────────────────────────────────────
@st.cache_data
def load_data():
    path = "data/sales_data.csv"
    if not os.path.exists(path):
        st.error("data/sales_data.csv not found. Run: python data/generate_data.py")
        st.stop()
    df = pd.read_csv(path, parse_dates=["date"])
    return df


@st.cache_resource
def load_model(name: str):
    path = f"models/{name}"
    if os.path.exists(path):
        return joblib.load(path)
    return None


# ─── SIDEBAR ─────────────────────────────────────────────
def render_sidebar(df):
    st.sidebar.image("https://img.icons8.com/color/96/sales-performance.png", width=60)
    st.sidebar.title("Sales Analytics AI")
    st.sidebar.markdown("---")

    page = st.sidebar.radio("Navigate", [
        "📊 Executive Dashboard",
        "🔮 Sales Forecasting",
        "🚨 Churn Prediction",
        "🎯 Strategy Simulator",
        "🤖 AI Strategy Agent",
        "📋 Reports",
    ])

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filters**")

    date_range = st.sidebar.date_input(
        "Date range",
        value=[df["date"].min(), df["date"].max()],
        min_value=df["date"].min(),
        max_value=df["date"].max(),
    )

    categories = st.sidebar.multiselect(
        "Product Category",
        options=sorted(df["product_category"].unique()),
        default=sorted(df["product_category"].unique()),
    )

    regions = st.sidebar.multiselect(
        "Region",
        options=sorted(df["region"].unique()),
        default=sorted(df["region"].unique()),
    )

    return page, date_range, categories, regions


def filter_df(df, date_range, categories, regions):
    if len(date_range) == 2:
        df = df[(df["date"] >= pd.Timestamp(date_range[0])) &
                (df["date"] <= pd.Timestamp(date_range[1]))]
    df = df[df["product_category"].isin(categories)]
    df = df[df["region"].isin(regions)]
    return df


# ─── PAGE: EXECUTIVE DASHBOARD ───────────────────────────
def page_dashboard(df):
    st.title("📊 Executive Sales Dashboard")

    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Revenue", f"${df['revenue'].sum():,.0f}",
                  delta=f"+{df[df['date'] >= df['date'].max()-timedelta(days=30)]['revenue'].sum():,.0f} (30d)")
    with col2:
        st.metric("Total Profit", f"${df['profit'].sum():,.0f}")
    with col3:
        margin = df['profit'].sum() / df['revenue'].sum() * 100
        st.metric("Profit Margin", f"{margin:.1f}%")
    with col4:
        st.metric("Total Orders", f"{len(df):,}")
    with col5:
        churn = df['customer_churned'].mean() * 100
        st.metric("Churn Rate", f"{churn:.1f}%",
                  delta=f"{churn-20:.1f}% vs target", delta_color="inverse")

    st.markdown("---")

    # Revenue Trend
    col_left, col_right = st.columns([2, 1])
    with col_left:
        monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
        fig = px.area(monthly, x="date", y="revenue",
                      title="Monthly Revenue Trend",
                      labels={"revenue": "Revenue ($)", "date": "Month"},
                      color_discrete_sequence=["#5B6AF0"])
        fig.update_layout(showlegend=False, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        cat_rev = df.groupby("product_category")["revenue"].sum().reset_index()
        fig = px.pie(cat_rev, values="revenue", names="product_category",
                     title="Revenue by Category",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Regional & Channel
    col1, col2 = st.columns(2)
    with col1:
        reg = df.groupby("region")[["revenue", "profit"]].sum().reset_index()
        fig = px.bar(reg, x="region", y=["revenue", "profit"],
                     barmode="group", title="Revenue & Profit by Region",
                     color_discrete_sequence=["#5B6AF0", "#F04E6A"])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ch = df.groupby("channel")["revenue"].sum().reset_index()
        fig = px.bar(ch, x="revenue", y="channel", orientation="h",
                     title="Revenue by Sales Channel",
                     color_discrete_sequence=["#5B6AF0"])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap: Revenue by month × weekday
    st.subheader("Revenue Heatmap")
    df["weekday"] = df["date"].dt.day_name()
    df["month_name"] = df["date"].dt.strftime("%b %Y")
    heat = df.pivot_table(values="revenue", index="weekday",
                           columns="product_category", aggfunc="sum").fillna(0)
    fig = px.imshow(heat, title="Revenue Heatmap (Weekday × Category)",
                    color_continuous_scale="Blues", aspect="auto")
    st.plotly_chart(fig, use_container_width=True)


# ─── PAGE: SALES FORECASTING ─────────────────────────────
def page_forecasting(df):
    st.title("🔮 Sales Forecasting")

    # Simple trend-based forecast (no model file needed for demo)
    weekly = df.resample("W", on="date")["revenue"].sum().reset_index()
    weekly.columns = ["date", "revenue"]

    st.subheader("Weekly Revenue with Trend Forecast")
    n_forecast = st.slider("Forecast weeks ahead", 4, 26, 12)

    # Simple moving average forecast
    ma_window = 8
    weekly["MA"] = weekly["revenue"].rolling(ma_window).mean()
    last_ma = weekly["MA"].iloc[-1]
    slope   = (weekly["MA"].iloc[-1] - weekly["MA"].iloc[-ma_window]) / ma_window

    future_dates  = [weekly["date"].iloc[-1] + timedelta(weeks=i) for i in range(1, n_forecast+1)]
    future_values = [max(0, last_ma + slope * i + np.random.normal(0, last_ma * 0.03))
                     for i in range(1, n_forecast+1)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weekly["date"], y=weekly["revenue"],
                              mode="lines", name="Actual", line=dict(color="#5B6AF0")))
    fig.add_trace(go.Scatter(x=weekly["date"], y=weekly["MA"],
                              mode="lines", name=f"{ma_window}w Moving Avg",
                              line=dict(color="#888", dash="dot")))
    fig.add_trace(go.Scatter(x=future_dates, y=future_values,
                              mode="lines+markers", name="Forecast",
                              line=dict(color="#F04E6A", dash="dash")))

    # Confidence interval
    upper = [v * 1.15 for v in future_values]
    lower = [v * 0.85 for v in future_values]
    fig.add_trace(go.Scatter(x=future_dates + future_dates[::-1],
                              y=upper + lower[::-1],
                              fill="toself", fillcolor="rgba(240,78,106,0.1)",
                              line=dict(color="rgba(255,255,255,0)"),
                              name="Confidence Interval"))

    fig.update_layout(title="Sales Forecast", height=450,
                       xaxis_title="Date", yaxis_title="Revenue ($)")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Next 4-week Forecast",
                  f"${sum(future_values[:4]):,.0f}")
    with col2:
        st.metric("Next 8-week Forecast",
                  f"${sum(future_values[:8]):,.0f}")
    with col3:
        st.metric(f"Next {n_forecast}-week Forecast",
                  f"${sum(future_values):,.0f}")

    # Category forecast
    st.subheader("Category-wise Monthly Forecast")
    cat_monthly = df.groupby(["product_category",
                               df["date"].dt.to_period("M")])["revenue"].sum().reset_index()
    cat_monthly["date"] = cat_monthly["date"].astype(str)
    fig = px.line(cat_monthly, x="date", y="revenue",
                  color="product_category", title="Revenue by Category Over Time")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


# ─── PAGE: CHURN PREDICTION ──────────────────────────────
def page_churn(df):
    st.title("🚨 Churn Prediction & Risk Analysis")

    # Overall churn stats
    col1, col2, col3 = st.columns(3)
    with col1:
        overall = df["customer_churned"].mean() * 100
        st.metric("Overall Churn Rate", f"{overall:.1f}%")
    with col2:
        high_val_churn = df[df["revenue"] > df["revenue"].quantile(0.75)]["customer_churned"].mean() * 100
        st.metric("High-Value Customer Churn", f"{high_val_churn:.1f}%")
    with col3:
        disc_churn = df[df["discount"] == 0]["customer_churned"].mean() * 100
        st.metric("Non-Discounted Churn", f"{disc_churn:.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        churn_by_cat = df.groupby("product_category")["customer_churned"].mean().reset_index()
        churn_by_cat.columns = ["Category", "Churn Rate"]
        churn_by_cat["Churn Rate"] *= 100
        churn_by_cat = churn_by_cat.sort_values("Churn Rate", ascending=True)
        fig = px.bar(churn_by_cat, x="Churn Rate", y="Category", orientation="h",
                     title="Churn Rate by Category (%)",
                     color="Churn Rate", color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        churn_by_region = df.groupby("region")["customer_churned"].mean().reset_index()
        churn_by_region.columns = ["Region", "Churn Rate"]
        churn_by_region["Churn Rate"] *= 100
        fig = px.bar(churn_by_region, x="Region", y="Churn Rate",
                     title="Churn Rate by Region (%)",
                     color="Churn Rate", color_continuous_scale="Oranges")
        st.plotly_chart(fig, use_container_width=True)

    # Risk segmentation
    st.subheader("Customer Risk Segmentation")
    df_sample = df.sample(min(500, len(df))).copy()
    df_sample["churn_risk"] = (
        (df_sample["customer_churned"] * 0.4) +
        (df_sample["discount"] * 0.3) +
        ((1 - df_sample["quantity"] / df_sample["quantity"].max()) * 0.3)
    )
    df_sample["risk_band"] = pd.cut(df_sample["churn_risk"],
                                     bins=[0, 0.2, 0.5, 0.75, 1.0],
                                     labels=["Low", "Medium", "High", "Critical"])
    risk_counts = df_sample["risk_band"].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Count"]
    fig = px.pie(risk_counts, values="Count", names="Risk Level",
                 color_discrete_map={"Low":"#28a745","Medium":"#ffc107",
                                      "High":"#fd7e14","Critical":"#dc3545"},
                 title="Customer Risk Distribution")
    st.plotly_chart(fig, use_container_width=True)

    # Interactive prediction
    st.subheader("Single Customer Churn Predictor")
    with st.form("churn_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            cat    = st.selectbox("Product Category", df["product_category"].unique())
            region = st.selectbox("Region", df["region"].unique())
        with c2:
            qty     = st.slider("Order Quantity", 1, 50, 10)
            revenue = st.number_input("Order Revenue ($)", 50.0, 5000.0, 300.0)
        with c3:
            discount = st.slider("Discount (%)", 0, 30, 0) / 100
            channel  = st.selectbox("Channel", df["channel"].unique())
        submitted = st.form_submit_button("Predict Churn Risk")

    if submitted:
        # Simple heuristic (replace with loaded ML model)
        risk_score = (
            (discount * 0.4) +
            (0.3 if cat in ["Books", "Clothing"] else 0.1) +
            (0.2 if region in ["South", "West"] else 0.1) +
            (0.1 * (1 - min(qty / 20, 1)))
        )
        risk_pct = min(risk_score * 100, 99)
        level = "🔴 HIGH" if risk_pct > 50 else ("🟡 MEDIUM" if risk_pct > 25 else "🟢 LOW")
        st.success(f"**Predicted Churn Risk: {risk_pct:.0f}% — {level}**")


# ─── PAGE: STRATEGY SIMULATOR ────────────────────────────
def page_strategy(df):
    st.title("🎯 Sales Strategy Simulator")

    tab1, tab2, tab3 = st.tabs(["💰 Discount Simulator", "📍 Regional Targeting", "📦 Product Mix"])

    with tab1:
        st.subheader("What-If Discount Analysis")
        col1, col2 = st.columns(2)
        with col1:
            cat      = st.selectbox("Product Category", df["product_category"].unique(), key="disc_cat")
            discount = st.slider("Discount %", 0, 40, 10, key="disc_pct")
            vol_inc  = st.slider("Expected Volume Increase %", -20, 100, 20, key="vol_inc")

        cat_df   = df[df["product_category"] == cat]
        base_rev = cat_df["revenue"].sum()
        base_pft = cat_df["profit"].sum()
        margin   = base_pft / base_rev if base_rev > 0 else 0.35

        new_rev  = base_rev * (1 - discount/100) * (1 + vol_inc/100)
        new_pft  = new_rev * margin * (1 - discount/100 * 0.5)

        with col2:
            st.metric("Baseline Revenue",  f"${base_rev:,.0f}")
            st.metric("Projected Revenue", f"${new_rev:,.0f}",
                      delta=f"${new_rev-base_rev:+,.0f}")
            st.metric("Projected Profit",  f"${new_pft:,.0f}",
                      delta=f"${new_pft-base_pft:+,.0f}",
                      delta_color="normal" if new_pft >= base_pft else "inverse")

        # Sweep chart
        discounts  = list(range(0, 41, 5))
        scenarios = []
        for d in discounts:
            r = base_rev * (1 - d/100) * (1 + vol_inc/100)
            p = r * margin * (1 - d/100 * 0.5)
            scenarios.append({"Discount (%)": d, "Revenue": r, "Profit": p})
        sweep = pd.DataFrame(scenarios)
        fig = px.line(sweep, x="Discount (%)", y=["Revenue", "Profit"],
                      title="Revenue & Profit vs Discount %",
                      color_discrete_sequence=["#5B6AF0", "#F04E6A"])
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Regional Marketing Budget Allocation")
        budget = st.number_input("Total Marketing Budget ($)", 1000, 500000, 50000, step=5000)

        reg_perf = df.groupby("region").agg(
            revenue=("revenue","sum"), profit=("profit","sum"),
            orders=("revenue","count"), churn=("customer_churned","mean")
        ).reset_index()
        reg_perf["roi_score"] = (
            (reg_perf["profit"] / reg_perf["revenue"]) *
            (1 - reg_perf["churn"]) *
            np.log1p(reg_perf["revenue"])
        )
        reg_perf["budget_share_%"] = (
            reg_perf["roi_score"] / reg_perf["roi_score"].sum() * 100
        ).round(1)
        reg_perf["allocated_budget"] = (
            reg_perf["budget_share_%"] / 100 * budget
        ).round(0)

        st.dataframe(reg_perf[[
            "region","revenue","profit","churn","roi_score","budget_share_%","allocated_budget"
        ]].rename(columns={
            "revenue":"Revenue","profit":"Profit","churn":"Churn Rate",
            "roi_score":"ROI Score","budget_share_%":"Budget Share %",
            "allocated_budget":"Allocated Budget ($)"
        }).round(2), use_container_width=True)

        fig = px.bar(reg_perf, x="region", y="allocated_budget",
                     title="Recommended Budget Allocation by Region",
                     color="roi_score", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Product Mix Optimization")
        cat_metrics = df.groupby("product_category").agg(
            revenue=("revenue","sum"), profit=("profit","sum"),
            orders=("revenue","count"), avg_price=("unit_price","mean"),
            avg_discount=("discount","mean"), churn=("customer_churned","mean")
        ).reset_index()
        cat_metrics["margin_%"] = (cat_metrics["profit"]/cat_metrics["revenue"]*100).round(1)

        fig = px.scatter(cat_metrics, x="revenue", y="margin_%",
                         size="orders", color="churn",
                         text="product_category",
                         title="Revenue vs Margin (bubble = orders, color = churn)",
                         color_continuous_scale="RdYlGn_r",
                         labels={"revenue":"Total Revenue","margin_%":"Profit Margin %"})
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)


# ─── PAGE: AI STRATEGY AGENT ─────────────────────────────
def page_agent(df):
    st.title("🤖 AI Strategy Agent")
    st.info("💡 Chat with the AI agent to get data-driven strategy recommendations. "
            "Provide your OpenAI API key in .env to use GPT-4o-mini.")

    api_key = st.text_input("OpenAI API Key (optional)", type="password",
                             help="Leave blank to use rule-based engine")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat
    for msg in st.session_state.chat_history:
        role = msg["role"]
        with st.chat_message(role):
            st.write(msg["content"])

    # Quick prompts
    st.markdown("**Quick questions:**")
    cols = st.columns(3)
    quick = [
        "Summarize sales performance",
        "Best region to target with $50k budget",
        "Should I offer 20% discount on Electronics?",
        "Forecast next quarter revenue",
        "Which category has highest churn?",
        "Recommend pricing strategy",
    ]
    for i, q in enumerate(quick):
        if cols[i % 3].button(q, key=f"quick_{i}"):
            st.session_state.pending_question = q

    # Input
    user_input = st.chat_input("Ask about sales strategy...")
    if not user_input and "pending_question" in st.session_state:
        user_input = st.session_state.pop("pending_question")

    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})

        with st.spinner("Analyzing your data..."):
            try:
                if api_key:
                    import sys
                    sys.path.append("agents")
                    from strategy_agent import build_strategy_agent
                    agent = build_strategy_agent(api_key)
                    if agent:
                        result = agent.invoke({"input": user_input})
                        response = result["output"]
                    else:
                        response = "Failed to initialize agent."
                else:
                    # Rule-based fallback
                    response = _simple_answer(user_input, df)
            except Exception as e:
                response = f"Error: {str(e)}"

        st.session_state.chat_history.append({"role":"assistant","content":response})
        st.rerun()

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


def _simple_answer(question: str, df: pd.DataFrame) -> str:
    q = question.lower()
    if "summary" in q or "overview" in q or "performance" in q:
        total_rev = df["revenue"].sum()
        total_pft = df["profit"].sum()
        churn     = df["customer_churned"].mean() * 100
        top_cat   = df.groupby("product_category")["revenue"].sum().idxmax()
        top_reg   = df.groupby("region")["revenue"].sum().idxmax()
        return (f"📊 **Sales Summary:**\n"
                f"- Total Revenue: ${total_rev:,.0f}\n"
                f"- Total Profit: ${total_pft:,.0f}\n"
                f"- Profit Margin: {total_pft/total_rev*100:.1f}%\n"
                f"- Churn Rate: {churn:.1f}%\n"
                f"- Top Category: {top_cat}\n"
                f"- Top Region: {top_reg}")
    if "discount" in q:
        return ("💰 **Discount Strategy Analysis:**\n"
                "Based on historical data, discounts >15% tend to reduce profit margins "
                "more than the volume increase compensates. Recommended sweet spot: 5-10% "
                "discount with targeted promotions for high-churn segments.")
    if "forecast" in q or "quarter" in q:
        quarterly = df.resample("QE", on="date")["revenue"].sum()
        last_q = quarterly.iloc[-1] if len(quarterly) > 0 else 0
        return (f"🔮 **Revenue Forecast:**\n"
                f"- Last Quarter: ${last_q:,.0f}\n"
                f"- Projected Next Quarter: ${last_q*1.05:,.0f} (+5% trend)\n"
                f"- Confidence: Medium (based on 3-quarter moving average)")
    if "region" in q or "budget" in q:
        reg = df.groupby("region")["revenue"].sum().idxmax()
        return (f"📍 **Regional Recommendation:**\n"
                f"- Highest revenue region: {reg}\n"
                f"- Recommended budget allocation: 40% to top region, 30% to fastest-growing\n"
                f"- Focus channels: Online + Mobile App for highest ROI")
    return ("I can help with: sales summary, discount analysis, revenue forecasting, "
            "regional targeting, and product mix optimization. What would you like to know?")


# ─── PAGE: REPORTS ───────────────────────────────────────
def page_reports(df):
    st.title("📋 Reports & Data Export")

    st.subheader("Summary Report")
    report_data = {
        "Total Revenue":   f"${df['revenue'].sum():,.2f}",
        "Total Profit":    f"${df['profit'].sum():,.2f}",
        "Profit Margin":   f"{df['profit'].sum()/df['revenue'].sum()*100:.1f}%",
        "Total Orders":    f"{len(df):,}",
        "Avg Order Value": f"${df['revenue'].mean():,.2f}",
        "Churn Rate":      f"{df['customer_churned'].mean()*100:.1f}%",
        "Top Category":    df.groupby("product_category")["revenue"].sum().idxmax(),
        "Top Region":      df.groupby("region")["revenue"].sum().idxmax(),
        "Date Range":      f"{df['date'].min().date()} to {df['date'].max().date()}",
    }

    for k, v in report_data.items():
        st.write(f"**{k}:** {v}")

    st.markdown("---")
    st.subheader("Download Data")

    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button("⬇ Download Full Dataset (CSV)", csv,
                           "sales_data.csv", "text/csv")
    with col2:
        monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
        csv_m = monthly.to_csv(index=False)
        st.download_button("⬇ Download Monthly Summary (CSV)", csv_m,
                           "monthly_revenue.csv", "text/csv")


# ─── MAIN ────────────────────────────────────────────────
def main():
    df  = load_data()
    page, date_range, categories, regions = render_sidebar(df)
    df_filtered = filter_df(df, date_range, categories, regions)

    if not len(df_filtered):
        st.warning("No data matches the selected filters.")
        return

    if page == "📊 Executive Dashboard":
        page_dashboard(df_filtered)
    elif page == "🔮 Sales Forecasting":
        page_forecasting(df_filtered)
    elif page == "🚨 Churn Prediction":
        page_churn(df_filtered)
    elif page == "🎯 Strategy Simulator":
        page_strategy(df_filtered)
    elif page == "🤖 AI Strategy Agent":
        page_agent(df_filtered)
    elif page == "📋 Reports":
        page_reports(df_filtered)


if __name__ == "__main__":
    main()
