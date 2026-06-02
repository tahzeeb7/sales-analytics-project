import argparse
import subprocess
import pandas as pd
import numpy as np
import random

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║     PREDICTIVE SALES ANALYTICS & STRATEGY SIMULATION        ║
║     Final Year Project — Business Intelligence + ML/DL      ║
╚══════════════════════════════════════════════════════════════╝
"""


# ==================================================
# STEP 1 - DATA GENERATION
# ==================================================
def step_generate_data():

    print("\n[STEP 1] Generating Sales Data...")

    try:
        import generate_data

        if hasattr(generate_data, "main"):
            generate_data.main()

        print("✓ Data generated successfully")

    except Exception as e:
        print("✗ Data generation failed")
        print(e)


# ==================================================
# STEP 2 - EDA
# ==================================================
def step_eda():

    print("\n[STEP 2] Running EDA...")

    try:
        from preprocessing import (
            load_data,
            basic_eda,
            engineer_features,
            plot_eda
        )

        df = load_data("sales_data.csv")

        basic_eda(df)

        df = engineer_features(df)

        plot_eda(df, save_dir="reports")

        print("✓ EDA Complete")

    except Exception as e:
        print("✗ EDA Failed")
        print(e)


# ==================================================
# STEP 3 - ML
# ==================================================
def step_ml():

    print("\n[STEP 3] Training ML Models...")

    try:

        from preprocessing import (
            load_data,
            engineer_features,
            encode_and_scale,
            split_data
        )

        from ml_models import (
            train_revenue_models,
            train_churn_models
        )

        df = load_data("sales_data.csv")

        df = engineer_features(df)

        df_enc, encoders, scaler = encode_and_scale(df)

        # Revenue
        X_tr, X_te, y_tr, y_te, feats = split_data(
            df_enc,
            target="revenue"
        )

        train_revenue_models(
            X_tr,
            X_te,
            y_tr,
            y_te,
            feats
        )

        # Churn
        X_tr2, X_te2, y_tr2, y_te2, feats2 = split_data(
            df_enc,
            target="customer_churned"
        )

        train_churn_models(
            X_tr2,
            X_te2,
            y_tr2,
            y_te2,
            feats2
        )

        print("✓ ML Training Complete")

    except Exception as e:
        print("✗ ML Failed")
        print(e)


# ==================================================
# STEP 4 - DEEP LEARNING
# ==================================================
def step_dl():

    print("\n[STEP 4] Deep Learning...")

    try:

        import tensorflow as tf

        print("TensorFlow:", tf.__version__)

        from preprocessing import load_data, engineer_features

        from deep_learning import (
            prepare_time_series,
            build_lstm_model,
            train_deep_model,
            evaluate_deep_model
        )

        df = load_data("sales_data.csv")

        df = engineer_features(df)

        LOOK_BACK = 30

        X_tr, X_te, y_tr, y_te, scaler, ts = (
            prepare_time_series(
                df,
                freq="W",
                look_back=LOOK_BACK
            )
        )

        model = build_lstm_model(LOOK_BACK)

        model, history = train_deep_model(
            model,
            X_tr,
            y_tr,
            X_te,
            y_te,
            "lstm",
            epochs=20
        )

        results = evaluate_deep_model(
            model,
            X_te,
            y_te,
            scaler,
            "lstm"
        )

        print("✓ DL Complete")

    except ImportError:
        print("TensorFlow not installed")
        print("pip install tensorflow")

    except Exception as e:
        print(e)


# ==================================================
# STEP 5 - DASHBOARD
# ==================================================
def step_dashboard():

    print("\nLaunching Dashboard...")

    subprocess.run([
        "streamlit",
        "run",
        "app.py"
    ])


# ==================================================
# STEP 6 - API
# ==================================================
def step_api():

    print("\nLaunching API...")

    subprocess.run([
        "uvicorn",
        "api:app",
        "--reload",
        "--port",
        "8000"
    ])


# ==================================================
# MAIN
# ==================================================
def main():

    print(BANNER)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--steps",
        nargs="+",
        default=["data", "eda", "ml"],
        choices=[
            "all",
            "data",
            "eda",
            "ml",
            "dl",
            "dashboard",
            "api"
        ]
    )

    args = parser.parse_args()

    steps = args.steps

    if "all" in steps:
        steps = [
            "data",
            "eda",
            "ml",
            "dl"
        ]

    STEP_MAP = {
        "data": step_generate_data,
        "eda": step_eda,
        "ml": step_ml,
        "dl": step_dl,
        "dashboard": step_dashboard,
        "api": step_api
    }

    for step in steps:
        STEP_MAP[step]()

    print("\nPipeline Finished")


if __name__ == "__main__":
    main()