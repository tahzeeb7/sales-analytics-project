"""
run_pipeline.py
===============
Master script to run the full ML + BI pipeline end-to-end.
Usage: python run_pipeline.py [--steps all|data|eda|ml|dl|dashboard]
"""

import argparse
import os
import sys
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║     PREDICTIVE SALES ANALYTICS & STRATEGY SIMULATION        ║
║     Final Year Project — Business Intelligence + ML/DL       ║
╚══════════════════════════════════════════════════════════════╝
"""


def step_generate_data():
    print("\n[STEP 1] Generating synthetic sales data...")
    from data.generate_data import generate_record
    import pandas as pd, numpy as np, random

    np.random.seed(42); random.seed(42)
    from data.generate_data import (
        N_RECORDS, START_DATE, END_DATE, PRODUCTS, REGIONS,
        CHANNELS, SALESPERSON, random_date, seasonal_factor, OUTPUT_FILE
    )
    records = [generate_record(i) for i in range(1, N_RECORDS + 1)]
    df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    df["revenue_band"] = pd.cut(df["revenue"],
                                 bins=[0, 200, 500, 1000, 5000, np.inf],
                                 labels=["XS","S","M","L","XL"])
    df["is_discounted"] = (df["discount"] > 0).astype(int)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"  ✓ Generated {len(df):,} records → {OUTPUT_FILE}")


def step_eda():
    print("\n[STEP 2] Running EDA & Preprocessing...")
    from preprocessing import load_data, basic_eda, engineer_features, plot_eda

    df = load_data("data/sales_data.csv")
    basic_eda(df)
    df = engineer_features(df)
    plot_eda(df, save_dir="reports")
    print("  ✓ EDA complete. Plots saved to reports/")


def step_ml():
    print("\n[STEP 3] Training ML Models...")
    from preprocessing import load_data, engineer_features, encode_and_scale, split_data
    from ml_models import train_revenue_models, train_churn_models

    df     = load_data("data/sales_data.csv")
    df     = engineer_features(df)
    df_enc, encoders, scaler = encode_and_scale(df)

    # Revenue prediction
    X_tr, X_te, y_tr, y_te, feats = split_data(df_enc, target="revenue")
    rev_results, _ = train_revenue_models(X_tr, X_te, y_tr, y_te, feats)

    # Churn classification
    X_tr2, X_te2, y_tr2, y_te2, feats2 = split_data(df_enc, target="customer_churned")
    churn_results, _ = train_churn_models(X_tr2, X_te2, y_tr2, y_te2, feats2)

    print("  ✓ ML models trained and saved to models/")


def step_dl():
    print("\n[STEP 4] Training Deep Learning Models (LSTM/GRU)...")
    try:
        import tensorflow as tf
        print(f"  TensorFlow version: {tf.__version__}")
    except ImportError:
        print("  ⚠ TensorFlow not installed. Skipping DL step.")
        print("  Install with: pip install tensorflow")
        return

    from preprocessing import load_data, engineer_features
    from deep_learning import prepare_time_series, build_lstm_model, train_deep_model, evaluate_deep_model
    import pandas as pd

    df  = load_data("data/sales_data.csv")
    df  = engineer_features(df)
    df["date"] = pd.to_datetime(df["date"])

    LOOK_BACK = 30
    X_tr, X_te, y_tr, y_te, scaler, ts = prepare_time_series(df, freq="W", look_back=LOOK_BACK)

    lstm = build_lstm_model(LOOK_BACK)
    lstm, hist = train_deep_model(lstm, X_tr, y_tr, X_te, y_te, "lstm", epochs=50)
    res = evaluate_deep_model(lstm, X_te, y_te, scaler, "lstm")

    print(f"  ✓ LSTM R² = {res.get('R2',0):.4f}")
    print("  ✓ DL models saved to models/")


def step_dashboard():
    print("\n[STEP 5] Launching Streamlit Dashboard...")
    print("  URL: http://localhost:8501")
    print("  Press Ctrl+C to stop\n")
    subprocess.run(["streamlit", "run", "dashboard/app.py", "--server.port=8501"])


def step_api():
    print("\n[STEP 6] Launching FastAPI Backend...")
    print("  URL: http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("  Press Ctrl+C to stop\n")
    subprocess.run(["uvicorn", "src.api:app", "--reload", "--port=8000"])


# ─── CLI ─────────────────────────────────────────────────

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Sales Analytics Pipeline Runner"
    )
    parser.add_argument(
        "--steps", nargs="+",
        default=["data","eda","ml"],
        choices=["all","data","eda","ml","dl","dashboard","api"],
        help="Steps to run"
    )
    args = parser.parse_args()
    steps = args.steps
    if "all" in steps:
        steps = ["data","eda","ml","dl","dashboard"]

    STEP_MAP = {
        "data":      step_generate_data,
        "eda":       step_eda,
        "ml":        step_ml,
        "dl":        step_dl,
        "dashboard": step_dashboard,
        "api":       step_api,
    }

    for step in steps:
        if step in STEP_MAP:
            try:
                STEP_MAP[step]()
            except Exception as e:
                print(f"  ✗ Step '{step}' failed: {e}")
                import traceback; traceback.print_exc()

    print("\n=== Pipeline complete ===")
    print("Next steps:")
    print("  Dashboard: python run_pipeline.py --steps dashboard")
    print("  API:       python run_pipeline.py --steps api")
    print("  Agent:     python agents/strategy_agent.py")


if __name__ == "__main__":
    main()
