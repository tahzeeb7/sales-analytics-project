"""
agents/strategy_agent.py
========================
LangChain-powered AI agent for sales strategy simulation & recommendations.
Requires OPENAI_API_KEY in .env file.
"""

import os
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.tools import tool
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.schema import SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not installed. pip install langchain langchain-openai")


# ─── DATA CACHE (loaded once) ────────────────────────────

_df_cache: pd.DataFrame = None

def _get_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        try:
            _df_cache = pd.read_csv("data/sales_data.csv", parse_dates=["date"])
        except FileNotFoundError:
            # Generate minimal mock data if file missing
            _df_cache = pd.DataFrame({
                "product_category": ["Electronics", "Clothing", "Home Goods"] * 100,
                "region": ["North", "South", "East"] * 100,
                "channel": ["Online", "Retail Store"] * 150,
                "revenue": np.random.uniform(50, 2000, 300),
                "profit": np.random.uniform(10, 800, 300),
                "quantity": np.random.randint(1, 20, 300),
                "discount": np.random.choice([0, 0.05, 0.1, 0.15], 300),
                "customer_churned": np.random.choice([0, 1], 300, p=[0.82, 0.18]),
                "date": pd.date_range("2023-01-01", periods=300, freq="D"),
            })
    return _df_cache


# ─── LANGCHAIN TOOLS ─────────────────────────────────────

if LANGCHAIN_AVAILABLE:

    @tool
    def get_sales_summary(period: str = "all") -> str:
        """
        Returns a summary of sales KPIs.
        period can be: 'all', 'last_30', 'last_90', 'last_year'
        """
        df = _get_df()
        if period == "last_30":
            df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=30)]
        elif period == "last_90":
            df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=90)]
        elif period == "last_year":
            df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=365)]

        summary = {
            "total_revenue":   round(df["revenue"].sum(), 2),
            "total_profit":    round(df["profit"].sum(), 2),
            "avg_order_value": round(df["revenue"].mean(), 2),
            "total_orders":    len(df),
            "churn_rate":      round(df["customer_churned"].mean() * 100, 2),
            "top_category":    df.groupby("product_category")["revenue"].sum().idxmax(),
            "top_region":      df.groupby("region")["revenue"].sum().idxmax(),
            "top_channel":     df.groupby("channel")["revenue"].sum().idxmax(),
        }
        return json.dumps(summary, indent=2)


    @tool
    def simulate_discount_strategy(
        category: str,
        discount_pct: float,
        expected_volume_increase_pct: float
    ) -> str:
        """
        Simulates the revenue impact of applying a discount to a product category.
        Args:
            category: product category name (e.g. 'Electronics')
            discount_pct: discount percentage as decimal (e.g. 0.15 for 15%)
            expected_volume_increase_pct: expected increase in sales volume (e.g. 0.2 for 20%)
        """
        df = _get_df()
        cat_df = df[df["product_category"] == category]

        if cat_df.empty:
            return f"Category '{category}' not found. Available: {df['product_category'].unique().tolist()}"

        baseline_rev    = cat_df["revenue"].sum()
        baseline_profit = cat_df["profit"].sum()
        avg_margin      = (baseline_profit / baseline_rev) if baseline_rev > 0 else 0.35

        new_revenue = baseline_rev * (1 - discount_pct) * (1 + expected_volume_increase_pct)
        new_profit  = new_revenue * avg_margin * (1 - discount_pct * 0.5)
        rev_change  = new_revenue - baseline_rev
        profit_change = new_profit - baseline_profit

        result = {
            "category":             category,
            "discount_applied":     f"{discount_pct*100:.0f}%",
            "volume_increase":      f"{expected_volume_increase_pct*100:.0f}%",
            "baseline_revenue":     round(baseline_rev, 2),
            "projected_revenue":    round(new_revenue, 2),
            "revenue_change":       round(rev_change, 2),
            "revenue_change_pct":   round((rev_change / baseline_rev) * 100, 2),
            "baseline_profit":      round(baseline_profit, 2),
            "projected_profit":     round(new_profit, 2),
            "profit_change":        round(profit_change, 2),
            "recommendation":       "PROCEED" if profit_change > 0 else "RISKY — profit decreases",
        }
        return json.dumps(result, indent=2)


    @tool
    def get_regional_performance() -> str:
        """Returns revenue and profit performance broken down by region."""
        df = _get_df()
        summary = df.groupby("region").agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("revenue", "count"),
            avg_order=("revenue", "mean"),
            churn_rate=("customer_churned", "mean")
        ).round(2).reset_index()
        summary["profit_margin_pct"] = (summary["profit"] / summary["revenue"] * 100).round(2)
        return summary.to_json(orient="records", indent=2)


    @tool
    def recommend_target_segment(budget_usd: float) -> str:
        """
        Given a marketing budget, recommends the best target segment (region + category).
        Returns top 3 opportunities ranked by ROI potential.
        Args:
            budget_usd: marketing budget in USD
        """
        df = _get_df()
        seg = df.groupby(["region", "product_category"]).agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("revenue", "count"),
            churn=("customer_churned", "mean")
        ).reset_index()

        seg["margin"]  = seg["profit"] / seg["revenue"]
        seg["roi_score"] = seg["margin"] * (1 - seg["churn"]) * np.log1p(seg["revenue"])
        top3 = seg.nlargest(3, "roi_score")[
            ["region", "product_category", "revenue", "margin", "churn", "roi_score"]
        ].round(4)

        estimated_returns = []
        for _, row in top3.iterrows():
            est = budget_usd * (1 + row["roi_score"] * 0.5)
            estimated_returns.append(round(est, 2))

        top3["estimated_return_usd"] = estimated_returns
        return top3.to_json(orient="records", indent=2)


    @tool
    def forecast_next_quarter(method: str = "trend") -> str:
        """
        Forecasts next quarter revenue using trend extrapolation.
        method: 'trend' or 'seasonal'
        """
        df = _get_df()
        quarterly = df.resample("QE", on="date")["revenue"].sum().reset_index()
        quarterly.columns = ["quarter", "revenue"]

        if len(quarterly) < 3:
            return "Insufficient data for forecasting."

        last_3q   = quarterly["revenue"].values[-3:]
        avg_growth = (last_3q[-1] / last_3q[0]) ** (1 / 2) - 1
        forecast  = last_3q[-1] * (1 + avg_growth)

        result = {
            "last_quarter_revenue":  round(last_3q[-1], 2),
            "avg_quarterly_growth":  round(avg_growth * 100, 2),
            "next_quarter_forecast": round(forecast, 2),
            "confidence":            "Medium" if len(quarterly) >= 6 else "Low",
            "method":                method,
        }
        return json.dumps(result, indent=2)


# ─── AGENT BUILDER ───────────────────────────────────────

def build_strategy_agent(openai_api_key: str = None):
    if not LANGCHAIN_AVAILABLE:
        print("LangChain not available.")
        return None

    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("No OpenAI API key found. Set OPENAI_API_KEY in .env")
        return None

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=api_key,
    )

    tools = [
        get_sales_summary,
        simulate_discount_strategy,
        get_regional_performance,
        recommend_target_segment,
        forecast_next_quarter,
    ]

    system_prompt = """You are SalesAI, an expert Business Intelligence and Sales Strategy advisor.
You have access to real sales data through specialized tools.

Your role:
- Analyze sales performance and trends
- Simulate business strategies (discounts, regional focus, channel mix)
- Provide data-driven recommendations
- Explain insights in business language, not just numbers
- Always quantify the financial impact of your recommendations

When answering:
1. Always use the tools to fetch real data before answering
2. Provide specific numbers, not vague statements
3. Structure answers with: Current State → Insight → Recommendation → Expected Impact
4. Be concise and actionable
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=10,
    )

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )

    return agent_executor


# ─── SIMPLE RULE-BASED FALLBACK (no API key needed) ──────

class SimpleStrategyEngine:
    """
    Rule-based strategy engine for demo purposes (no API key needed).
    """

    def __init__(self, data_path: str = "data/sales_data.csv"):
        self.df = pd.read_csv(data_path, parse_dates=["date"])

    def query(self, question: str) -> str:
        q = question.lower()

        if any(k in q for k in ["summary", "overview", "performance", "kpi"]):
            return json.loads(get_sales_summary.func("all"))

        if "discount" in q or "promotion" in q:
            return ("Based on your data, Electronics with a 10% discount and "
                    "expected 20% volume increase is the most profitable promotion. "
                    "Run simulate_discount_strategy tool for custom scenarios.")

        if "region" in q:
            return json.loads(get_regional_performance.func())

        if "forecast" in q or "predict" in q or "next quarter" in q:
            return json.loads(forecast_next_quarter.func("trend"))

        if "segment" in q or "target" in q or "budget" in q:
            return json.loads(recommend_target_segment.func(10000.0))

        return ("I can help with: sales summary, discount simulation, "
                "regional performance, target segment recommendations, "
                "and revenue forecasting. What would you like to know?")


if __name__ == "__main__":
    print("=== Strategy Agent Demo ===\n")

    # Try with LangChain agent first, fall back to simple engine
    agent = build_strategy_agent()

    if agent:
        questions = [
            "Give me a sales performance summary for the last 90 days.",
            "Simulate a 15% discount on Electronics with 25% volume increase. Is it worth it?",
            "Which region should I prioritize with a $50,000 marketing budget?",
        ]
        for q in questions:
            print(f"\nQ: {q}")
            result = agent.invoke({"input": q})
            print(f"A: {result['output']}")
    else:
        print("Using simple rule-based engine (no API key).")
        engine = SimpleStrategyEngine()
        print(engine.query("Give me a sales overview"))
