"""
src/preprocessing.py
====================
Exploratory Data Analysis + full preprocessing pipeline.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings("ignore")


# ─── LOAD & BASIC INFO ───────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    print(f"Loaded {len(df):,} rows × {df.shape[1]} columns")
    return df


def basic_eda(df: pd.DataFrame):
    print("\n=== BASIC EDA ===")
    print(df.info())
    print("\nNull values:\n", df.isnull().sum())
    print("\nNumeric summary:\n", df.describe().round(2))
    print("\nRevenue by category:\n",
          df.groupby("product_category")["revenue"].agg(["sum","mean","count"]).round(2))
    print("\nRevenue by region:\n",
          df.groupby("region")["revenue"].agg(["sum","mean"]).round(2))


# ─── FEATURE ENGINEERING ─────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Time features
    df["date"]         = pd.to_datetime(df["date"])
    df["month_sin"]    = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"]    = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_num"]      = df["date"].dt.dayofweek
    df["is_weekend"]   = (df["dow_num"] >= 5).astype(int)
    df["days_in_month"]= df["date"].dt.days_in_month

    # Revenue lag features (requires sort by date)
    df = df.sort_values("date").reset_index(drop=True)
    df["revenue_lag1"] = df["revenue"].shift(1).fillna(0)
    df["revenue_lag7"] = df["revenue"].shift(7).fillna(0)

    # Profit margin
    df["profit_margin"] = (df["profit"] / df["revenue"].replace(0, np.nan)).fillna(0)

    # Revenue per unit
    df["revenue_per_unit"] = df["revenue"] / df["quantity"].replace(0, 1)

    return df


# ─── ENCODING & SCALING ──────────────────────────────────

CATEGORICAL_COLS = ["product_category", "region", "channel", "day_of_week"]
NUMERIC_COLS     = ["quantity", "unit_price", "discount", "revenue",
                    "profit", "profit_margin", "revenue_per_unit",
                    "month_sin", "month_cos", "is_weekend",
                    "revenue_lag1", "revenue_lag7"]


def encode_and_scale(df: pd.DataFrame):
    df = df.copy()
    encoders = {}

    for col in CATEGORICAL_COLS:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col].astype(str))
        encoders[col]    = le

    scaler = StandardScaler()
    df[NUMERIC_COLS] = scaler.fit_transform(df[NUMERIC_COLS])

    return df, encoders, scaler


# ─── TRAIN/TEST SPLIT ────────────────────────────────────

def split_data(df: pd.DataFrame, target: str = "revenue",
               test_size: float = 0.2):
    feature_cols = (
        [c + "_enc" for c in CATEGORICAL_COLS] +
        ["quantity", "unit_price", "discount", "profit_margin",
         "revenue_per_unit", "month_sin", "month_cos", "is_weekend",
         "revenue_lag1", "revenue_lag7", "year", "quarter"]
    )
    feature_cols = [c for c in feature_cols if c in df.columns]

    X = df[feature_cols]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, shuffle=False
    )
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    return X_train, X_test, y_train, y_test, feature_cols


# ─── EDA PLOTS ───────────────────────────────────────────

def plot_eda(df: pd.DataFrame, save_dir: str = "reports"):
    import os
    os.makedirs(save_dir, exist_ok=True)

    # Monthly revenue trend
    monthly = df.resample("ME", on="date")["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(monthly["date"], monthly["revenue"], marker="o", color="#5B6AF0", linewidth=2)
    ax.fill_between(monthly["date"], monthly["revenue"], alpha=0.15, color="#5B6AF0")
    ax.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Revenue ($)")
    plt.tight_layout()
    plt.savefig(f"{save_dir}/monthly_revenue.png", dpi=150)
    plt.close()

    # Revenue by category
    fig, ax = plt.subplots(figsize=(8, 4))
    cat_rev = df.groupby("product_category")["revenue"].sum().sort_values()
    cat_rev.plot(kind="barh", ax=ax, color="#5B6AF0")
    ax.set_title("Revenue by Product Category")
    plt.tight_layout()
    plt.savefig(f"{save_dir}/revenue_by_category.png", dpi=150)
    plt.close()

    # Correlation heatmap
    num_cols = ["quantity", "unit_price", "discount", "revenue", "profit"]
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(df[num_cols].corr(), annot=True, fmt=".2f",
                cmap="coolwarm", ax=ax, square=True)
    ax.set_title("Feature Correlation")
    plt.tight_layout()
    plt.savefig(f"{save_dir}/correlation_heatmap.png", dpi=150)
    plt.close()

    print(f"EDA plots saved to {save_dir}/")


if __name__ == "__main__":
    df = load_data("sales_data.csv")
    basic_eda(df)
    df = engineer_features(df)
    plot_eda(df)
    print("Preprocessing complete.")
