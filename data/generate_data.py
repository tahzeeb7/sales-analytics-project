"""
generate_data.py
================
Generates a realistic synthetic sales dataset for the project.
Run this first: python data/generate_data.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# ─── CONFIG ──────────────────────────────────────────────
N_RECORDS     = 5000
START_DATE    = datetime(2021, 1, 1)
END_DATE      = datetime(2024, 6, 30)
OUTPUT_FILE   = os.path.join(os.path.dirname(__file__), "sales_data.csv")

PRODUCTS = {
    "Electronics": {"base_price": 450, "margin": 0.28, "seasonal_boost": [11, 12]},
    "Clothing":    {"base_price": 75,  "margin": 0.55, "seasonal_boost": [3, 4, 9, 10]},
    "Home Goods":  {"base_price": 120, "margin": 0.42, "seasonal_boost": [5, 6]},
    "Sports":      {"base_price": 95,  "margin": 0.38, "seasonal_boost": [1, 6, 7, 8]},
    "Books":       {"base_price": 25,  "margin": 0.65, "seasonal_boost": []},
}

REGIONS     = ["North", "South", "East", "West", "Central"]
CHANNELS    = ["Online", "Retail Store", "Wholesale", "Mobile App"]
SALESPERSON = [f"SP_{i:03d}" for i in range(1, 41)]


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def seasonal_factor(month, boosts):
    if month in boosts:
        return np.random.uniform(1.3, 1.8)
    return np.random.uniform(0.7, 1.1)


def generate_record(i):
    date       = random_date(START_DATE, END_DATE)
    product    = random.choice(list(PRODUCTS.keys()))
    info       = PRODUCTS[product]
    region     = random.choice(REGIONS)
    channel    = random.choice(CHANNELS)
    salesperson= random.choice(SALESPERSON)

    base_qty   = np.random.poisson(8)
    s_factor   = seasonal_factor(date.month, info["seasonal_boost"])
    quantity   = max(1, int(base_qty * s_factor))

    discount   = round(random.choices([0, 0.05, 0.10, 0.15, 0.20],
                                       weights=[40, 25, 20, 10, 5])[0], 2)
    unit_price = round(info["base_price"] * np.random.uniform(0.85, 1.15), 2)
    revenue    = round(unit_price * quantity * (1 - discount), 2)
    profit     = round(revenue * info["margin"] * np.random.uniform(0.8, 1.2), 2)

    # Churn proxy: 1 = customer churned after this order
    churn = 1 if (random.random() < 0.18 + (discount == 0) * 0.05) else 0

    return {
        "transaction_id": f"TXN{i:06d}",
        "date":           date.strftime("%Y-%m-%d"),
        "year":           date.year,
        "month":          date.month,
        "quarter":        (date.month - 1) // 3 + 1,
        "day_of_week":    date.strftime("%A"),
        "product_category": product,
        "region":         region,
        "channel":        channel,
        "salesperson_id": salesperson,
        "quantity":       quantity,
        "unit_price":     unit_price,
        "discount":       discount,
        "revenue":        revenue,
        "profit":         profit,
        "customer_churned": churn,
    }


if __name__ == "__main__":
    print("Generating synthetic sales data...")
    records = [generate_record(i) for i in range(1, N_RECORDS + 1)]
    df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)

    # Add some derived BI columns
    df["revenue_band"] = pd.cut(df["revenue"],
                                 bins=[0, 200, 500, 1000, 5000, np.inf],
                                 labels=["XS", "S", "M", "L", "XL"])
    df["is_discounted"] = (df["discount"] > 0).astype(int)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"  Saved {len(df):,} records → {OUTPUT_FILE}")
    print(f"  Date range: {df['date'].min()} → {df['date'].max()}")
    print(f"  Total revenue: ${df['revenue'].sum():,.2f}")
    print("\nSample:")
    print(df.head(3).to_string())
