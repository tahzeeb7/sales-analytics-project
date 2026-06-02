"""
agents/strategy_agent.py
========================
LangChain-powered AI agent for sales strategy simulation & recommendations.
Fallback engine included (no API key required).
"""

import os
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# ─── SAFE DATA PATH ───────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "sales_data.csv"

# ─── LANGCHAIN IMPORT ─────────────────────────────────────
try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.tools import tool
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.memory import ConversationBufferWindowMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not installed. pip install langchain langchain-openai")


# ─── DATA CACHE ──────────────────────────────────────────

_df_cache = None

def _get_df():
    global _df_cache
    if _df_cache is None:
        try:
            _df_cache = pd.read_csv(DATA_PATH, parse_dates=["date"])
        except FileNotFoundError:
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


# ─── CORE BUSINESS LOGIC (NO LANGCHAIN DEPENDENCY) ───────

def sales_summary(period="all"):
    df = _get_df()

    if period == "last_30":
        df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=30)]
    elif period == "last_90":
        df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=90)]
    elif period == "last_year":
        df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=365)]

    return {
        "total_revenue": round(df["revenue"].sum(), 2),
        "total_profit": round(df["profit"].sum(), 2),
        "avg_order_value": round(df["revenue"].mean(), 2),
        "total_orders": len(df),
        "churn_rate": round(df["customer_churned"].mean() * 100, 2),
        "top_category": df.groupby("product_category")["revenue"].sum().idxmax(),
        "top_region": df.groupby("region")["revenue"].sum().idxmax(),
        "top_channel": df.groupby("channel")["revenue"].sum().idxmax(),
    }


def simulate_discount(category, discount_pct, volume_increase):
    df = _get_df()
    cat_df = df[df["product_category"] == category]

    if cat_df.empty:
        return {"error": f"Category '{category}' not found"}

    baseline_rev = cat_df["revenue"].sum()
    baseline_profit = cat_df["profit"].sum()
    avg_margin = baseline_profit / baseline_rev if baseline_rev else 0.35

    new_revenue = baseline_rev * (1 - discount_pct) * (1 + volume_increase)
    new_profit = new_revenue * avg_margin * (1 - discount_pct * 0.5)

    return {
        "category": category,
        "baseline_revenue": round(baseline_rev, 2),
        "projected_revenue": round(new_revenue, 2),
        "revenue_change_pct": round(((new_revenue - baseline_rev) / baseline_rev) * 100, 2),
        "baseline_profit": round(baseline_profit, 2),
        "projected_profit": round(new_profit, 2),
        "recommendation": "PROCEED" if new_profit > baseline_profit else "RISKY"
    }


def regional_performance():
    df = _get_df()

    summary = df.groupby("region").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("revenue", "count"),
        churn_rate=("customer_churned", "mean")
    ).reset_index()

    summary["profit_margin_pct"] = (summary["profit"] / summary["revenue"] * 100).round(2)
    return summary.to_dict(orient="records")


def target_segment(budget):
    df = _get_df()

    seg = df.groupby(["region", "product_category"]).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        churn=("customer_churned", "mean")
    ).reset_index()

    seg["margin"] = seg["profit"] / seg["revenue"]
    seg["score"] = seg["margin"] * (1 - seg["churn"]) * np.log1p(seg["revenue"])

    top = seg.nlargest(3, "score")

    results = []
    for _, row in top.iterrows():
        results.append({
            "region": row["region"],
            "category": row["product_category"],
            "score": round(row["score"], 4),
            "estimated_return": round(budget * (1 + row["score"] * 0.5), 2)
        })

    return results


def forecast():
    df = _get_df()

    quarterly = df.resample("QE", on="date")["revenue"].sum()

    if len(quarterly) < 3:
        return {"error": "Insufficient data"}

    last = quarterly.values[-3:]
    growth = (last[-1] / last[0]) ** (1/2) - 1
    forecast_val = last[-1] * (1 + growth)

    return {
        "last_quarter": round(last[-1], 2),
        "growth_pct": round(growth * 100, 2),
        "forecast": round(forecast_val, 2)
    }


# ─── LANGCHAIN WRAPPERS ──────────────────────────────────

if LANGCHAIN_AVAILABLE:

    @tool
    def get_sales_summary(period: str = "all"):
        return json.dumps(sales_summary(period), indent=2)

    @tool
    def simulate_discount_strategy(category: str, discount_pct: float, expected_volume_increase_pct: float):
        return json.dumps(simulate_discount(category, discount_pct, expected_volume_increase_pct), indent=2)

    @tool
    def get_regional_performance():
        return json.dumps(regional_performance(), indent=2)

    @tool
    def recommend_target_segment(budget_usd: float):
        return json.dumps(target_segment(budget_usd), indent=2)

    @tool
    def forecast_next_quarter(method: str = "trend"):
        return json.dumps(forecast(), indent=2)


# ─── AGENT BUILDER ───────────────────────────────────────

def build_strategy_agent():
    if not LANGCHAIN_AVAILABLE:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
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

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are SalesAI. Always use tools before answering."),
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

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )


# ─── FALLBACK ENGINE (NO LANGCHAIN) ──────────────────────

class SimpleStrategyEngine:

    def query(self, question: str):

        q = question.lower()

        if any(k in q for k in ["summary", "overview", "kpi"]):
            return sales_summary("all")

        if "discount" in q:
            return simulate_discount("Electronics", 0.1, 0.2)

        if "region" in q:
            return regional_performance()

        if "forecast" in q or "predict" in q:
            return forecast()

        if "segment" in q or "budget" in q:
            return target_segment(10000)

        return {
            "message": "Ask about summary, discount, region, forecast, or segment."
        }


# ─── MAIN ────────────────────────────────────────────────

if __name__ == "__main__":

    print("=== Strategy Agent Demo ===\n")

    agent = build_strategy_agent()

    if agent:
        questions = [
            "Give me a sales summary",
            "Simulate discount on Electronics",
            "Best region for $50k budget?"
        ]

        for q in questions:
            print("\nQ:", q)
            res = agent.invoke({"input": q})
            print("A:", res["output"])

    else:
        print("Using fallback engine...\n")
        engine = SimpleStrategyEngine()
        print(engine.query("Give me a sales overview"))