"""
src/api.py
==========
FastAPI REST API for serving ML model predictions.
Run: uvicorn src.api:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime

app = FastAPI(
    title="Sales Analytics AI — REST API",
    description="Predictive sales analytics endpoints.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── LOAD MODELS ─────────────────────────────────────────
_revenue_model = None
_churn_model   = None

def get_revenue_model():
    global _revenue_model
    if _revenue_model is None and os.path.exists("models/best_revenue_model.pkl"):
        _revenue_model = joblib.load("models/best_revenue_model.pkl")
    return _revenue_model

def get_churn_model():
    global _churn_model
    if _churn_model is None and os.path.exists("models/best_churn_model.pkl"):
        _churn_model = joblib.load("models/best_churn_model.pkl")
    return _churn_model


# ─── SCHEMAS ─────────────────────────────────────────────

class SalesPredictionRequest(BaseModel):
    quantity:          int   = Field(..., ge=1, le=1000,  description="Number of units")
    unit_price:        float = Field(..., ge=1,           description="Unit price in $")
    discount:          float = Field(0.0, ge=0, le=0.5,  description="Discount (0–0.5)")
    product_category:  str   = Field(...,                  description="Product category")
    region:            str   = Field(...,                  description="Sales region")
    channel:           str   = Field(...,                  description="Sales channel")
    month:             int   = Field(..., ge=1, le=12,    description="Month (1–12)")
    year:              int   = Field(2024,                 description="Year")


class ChurnRequest(BaseModel):
    quantity:          int   = Field(..., ge=1)
    unit_price:        float = Field(..., ge=1)
    discount:          float = Field(0.0, ge=0, le=0.5)
    product_category:  str
    region:            str
    channel:           str
    revenue:           float = Field(..., ge=0)
    month:             int   = Field(..., ge=1, le=12)


class ForecastRequest(BaseModel):
    horizon_weeks: int  = Field(12, ge=1, le=52)
    category:      Optional[str] = None
    region:        Optional[str] = None


class StrategySimRequest(BaseModel):
    category:               str
    discount_pct:           float = Field(..., ge=0, le=0.5)
    expected_volume_increase: float = Field(0.1, ge=-0.5, le=5.0)


# ─── FEATURE HELPERS ─────────────────────────────────────

CATEGORY_MAP = {"Electronics": 0, "Clothing": 1, "Home Goods": 2, "Sports": 3, "Books": 4}
REGION_MAP   = {"North": 0, "South": 1, "East": 2, "West": 3, "Central": 4}
CHANNEL_MAP  = {"Online": 0, "Retail Store": 1, "Wholesale": 2, "Mobile App": 3}
DOW_MAP      = {"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,"Friday":4,"Saturday":5,"Sunday":6}

def build_feature_vector(req) -> np.ndarray:
    cat_enc   = CATEGORY_MAP.get(req.product_category, 0)
    reg_enc   = REGION_MAP.get(req.region, 0)
    ch_enc    = CHANNEL_MAP.get(req.channel, 0)
    dow_enc   = 0
    month_sin = np.sin(2 * np.pi * req.month / 12)
    month_cos = np.cos(2 * np.pi * req.month / 12)
    revenue   = getattr(req, "revenue", req.unit_price * req.quantity * (1 - req.discount))
    profit_m  = 0.35
    rev_unit  = revenue / max(req.quantity, 1)
    quarter   = (req.month - 1) // 3 + 1

    return np.array([[
        cat_enc, reg_enc, ch_enc, dow_enc,
        req.quantity, req.unit_price, req.discount, profit_m,
        rev_unit, month_sin, month_cos, 0,
        0, 0, req.year, quarter
    ]])


# ─── ENDPOINTS ───────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Sales Analytics AI API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {
        "status":        "healthy",
        "timestamp":     datetime.utcnow().isoformat(),
        "revenue_model": os.path.exists("models/best_revenue_model.pkl"),
        "churn_model":   os.path.exists("models/best_churn_model.pkl"),
    }


@app.post("/predict/revenue", tags=["Predictions"])
def predict_revenue(req: SalesPredictionRequest):
    """Predict expected revenue for a given transaction."""
    model = get_revenue_model()

    if model is None:
        # Fallback: simple formula
        raw = req.unit_price * req.quantity * (1 - req.discount)
        return {"predicted_revenue": round(raw, 2), "model_used": "formula_fallback"}

    features = build_feature_vector(req)
    prediction = float(model.predict(features)[0])
    return {
        "predicted_revenue": round(prediction, 2),
        "model_used":        "ml_model",
        "input_summary": {
            "category": req.product_category,
            "region":   req.region,
            "qty":      req.quantity,
            "price":    req.unit_price,
        }
    }


@app.post("/predict/churn", tags=["Predictions"])
def predict_churn(req: ChurnRequest):
    """Predict churn probability for a customer transaction."""
    model = get_churn_model()

    if model is None:
        # Heuristic fallback
        risk = min(0.99, req.discount * 0.4 + 0.18 + (0.1 if req.category in ["Books"] else 0))
        return {"churn_probability": round(risk, 4),
                "churn_label": int(risk > 0.5), "model_used": "heuristic_fallback"}

    features = build_feature_vector(req)
    proba    = float(model.predict_proba(features)[0][1])
    label    = int(proba > 0.5)
    risk_level = "HIGH" if proba > 0.6 else ("MEDIUM" if proba > 0.3 else "LOW")

    return {
        "churn_probability": round(proba, 4),
        "churn_label":       label,
        "risk_level":        risk_level,
        "model_used":        "ml_model",
    }


@app.post("/simulate/strategy", tags=["Strategy"])
def simulate_strategy(req: StrategySimRequest):
    """Simulate the financial impact of a discount strategy."""
    try:
        df = pd.read_csv("data/sales_data.csv")
        cat_df = df[df["product_category"] == req.category]
        if cat_df.empty:
            raise HTTPException(404, f"Category '{req.category}' not found.")

        base_rev = float(cat_df["revenue"].sum())
        base_pft = float(cat_df["profit"].sum())
        margin   = base_pft / base_rev if base_rev > 0 else 0.35

        new_rev  = base_rev * (1 - req.discount_pct) * (1 + req.expected_volume_increase)
        new_pft  = new_rev * margin * (1 - req.discount_pct * 0.5)

        return {
            "category":           req.category,
            "discount_pct":       req.discount_pct,
            "volume_change_pct":  req.expected_volume_increase,
            "baseline_revenue":   round(base_rev, 2),
            "projected_revenue":  round(new_rev, 2),
            "revenue_change":     round(new_rev - base_rev, 2),
            "baseline_profit":    round(base_pft, 2),
            "projected_profit":   round(new_pft, 2),
            "profit_change":      round(new_pft - base_pft, 2),
            "recommendation":     "PROCEED" if new_pft > base_pft else "NOT RECOMMENDED",
        }
    except FileNotFoundError:
        raise HTTPException(500, "Data file not found.")


@app.get("/analytics/summary", tags=["Analytics"])
def get_summary():
    """Overall sales KPI summary."""
    try:
        df = pd.read_csv("data/sales_data.csv")
        return {
            "total_revenue":   round(float(df["revenue"].sum()), 2),
            "total_profit":    round(float(df["profit"].sum()), 2),
            "total_orders":    int(len(df)),
            "avg_order_value": round(float(df["revenue"].mean()), 2),
            "churn_rate":      round(float(df["customer_churned"].mean()), 4),
            "top_category":    df.groupby("product_category")["revenue"].sum().idxmax(),
            "top_region":      df.groupby("region")["revenue"].sum().idxmax(),
            "date_from":       df["date"].min(),
            "date_to":         df["date"].max(),
        }
    except FileNotFoundError:
        raise HTTPException(500, "Data file not found.")


@app.get("/analytics/by-category", tags=["Analytics"])
def get_by_category():
    df = pd.read_csv("data/sales_data.csv")
    result = df.groupby("product_category").agg(
        revenue=("revenue","sum"), profit=("profit","sum"),
        orders=("revenue","count"), avg_order=("revenue","mean"),
        churn_rate=("customer_churned","mean")
    ).round(2).reset_index()
    return result.to_dict(orient="records")


@app.get("/analytics/by-region", tags=["Analytics"])
def get_by_region():
    df = pd.read_csv("data/sales_data.csv")
    result = df.groupby("region").agg(
        revenue=("revenue","sum"), profit=("profit","sum"),
        orders=("revenue","count"), churn_rate=("customer_churned","mean")
    ).round(2).reset_index()
    return result.to_dict(orient="records")
