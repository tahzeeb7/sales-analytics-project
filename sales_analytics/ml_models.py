"""
src/ml_models.py
================
Train and evaluate classical ML models for:
  1. Revenue prediction (regression)
  2. Churn prediction (classification)
"""

import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, classification_report, roc_auc_score,
    confusion_matrix
)
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


# ─── REGRESSION: Revenue Prediction ──────────────────────

def train_revenue_models(X_train, X_test, y_train, y_test, feature_cols):
    """Train multiple regression models and compare performance."""

    models = {
        "Linear Regression":   LinearRegression(),
        "Ridge Regression":    Ridge(alpha=1.0),
        "Random Forest":       RandomForestRegressor(n_estimators=200, max_depth=12,
                                                      random_state=42, n_jobs=-1),
        "XGBoost":             XGBRegressor(n_estimators=300, max_depth=6,
                                             learning_rate=0.05, random_state=42,
                                             verbosity=0),
        "Gradient Boosting":   GradientBoostingRegressor(n_estimators=200,
                                                          max_depth=5,
                                                          random_state=42),
    }

    results = {}
    print("\n=== REVENUE PREDICTION MODELS ===")
    print(f"{'Model':<25} {'MAE':>10} {'RMSE':>10} {'R²':>8}")
    print("-" * 57)

    best_r2   = -np.inf
    best_model= None
    best_name = ""

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        mae  = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2   = r2_score(y_test, preds)

        print(f"{name:<25} {mae:>10.4f} {rmse:>10.4f} {r2:>8.4f}")
        results[name] = {"MAE": mae, "RMSE": rmse, "R2": r2,
                         "model": model, "predictions": preds}

        if r2 > best_r2:
            best_r2   = r2
            best_model= model
            best_name = name

    print(f"\nBest model: {best_name} (R² = {best_r2:.4f})")

    # Save best model
    joblib.dump(best_model, f"{MODEL_DIR}/best_revenue_model.pkl")
    joblib.dump(results,    f"{MODEL_DIR}/revenue_results.pkl")
    print(f"Models saved to {MODEL_DIR}/")

    # Feature importance (if tree model)
    if hasattr(best_model, "feature_importances_"):
        plot_feature_importance(best_model, feature_cols, "revenue")

    return results, best_model


# ─── CLASSIFICATION: Churn Prediction ────────────────────

def train_churn_models(X_train, X_test, y_train, y_test, feature_cols):
    """Train churn prediction classifiers."""

    models = {
        "Random Forest":   RandomForestClassifier(n_estimators=200, max_depth=10,
                                                   class_weight="balanced",
                                                   random_state=42, n_jobs=-1),
        "XGBoost":         XGBClassifier(n_estimators=300, max_depth=5,
                                          learning_rate=0.05, use_label_encoder=False,
                                          eval_metric="logloss", random_state=42,
                                          verbosity=0),
    }

    results = {}
    print("\n=== CHURN PREDICTION MODELS ===")
    print(f"{'Model':<20} {'Accuracy':>10} {'ROC-AUC':>10} {'F1(churn)':>12}")
    print("-" * 55)

    best_auc   = 0
    best_model = None
    best_name  = ""

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds      = model.predict(X_test)
        proba      = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, preds)
        auc = roc_auc_score(y_test, proba)
        report = classification_report(y_test, preds, output_dict=True)
        f1_churn = report.get("1", {}).get("f1-score", 0)

        print(f"{name:<20} {acc:>10.4f} {auc:>10.4f} {f1_churn:>12.4f}")
        results[name] = {"accuracy": acc, "roc_auc": auc,
                         "model": model, "predictions": preds, "probabilities": proba}

        if auc > best_auc:
            best_auc   = auc
            best_model = model
            best_name  = name

    print(f"\nBest model: {best_name} (AUC = {best_auc:.4f})")
    print("\nDetailed report (best model):")
    print(classification_report(y_test, best_model.predict(X_test)))

    joblib.dump(best_model, f"{MODEL_DIR}/best_churn_model.pkl")
    joblib.dump(results,    f"{MODEL_DIR}/churn_results.pkl")
    print(f"Models saved to {MODEL_DIR}/")

    if hasattr(best_model, "feature_importances_"):
        plot_feature_importance(best_model, feature_cols, "churn")

    return results, best_model


# ─── UTILITIES ───────────────────────────────────────────

def plot_feature_importance(model, feature_cols, task_name: str):
    imp = pd.Series(model.feature_importances_, index=feature_cols)
    top = imp.nlargest(15)

    fig, ax = plt.subplots(figsize=(8, 5))
    top.sort_values().plot(kind="barh", ax=ax, color="#5B6AF0")
    ax.set_title(f"Top 15 Feature Importances — {task_name.title()}")
    ax.set_xlabel("Importance")
    plt.tight_layout()
    os.makedirs("reports", exist_ok=True)
    plt.savefig(f"reports/feature_importance_{task_name}.png", dpi=150)
    plt.close()
    print(f"Feature importance plot saved.")


def plot_predictions_vs_actual(y_test, preds, title="Revenue: Predicted vs Actual"):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(y_test[:300], preds[:300], alpha=0.4, color="#5B6AF0", s=20)
    lims = [min(y_test.min(), preds.min()), max(y_test.max(), preds.max())]
    ax.plot(lims, lims, "r--", linewidth=1.5, label="Perfect fit")
    ax.set_xlabel("Actual"); ax.set_ylabel("Predicted")
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    os.makedirs("reports", exist_ok=True)
    plt.savefig("reports/predicted_vs_actual.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    # Quick smoke test
    from preprocessing import load_data, engineer_features, encode_and_scale, split_data

    df = load_data("data/sales_data.csv")
    df = engineer_features(df)
    df_enc, encoders, scaler = encode_and_scale(df)

    # Revenue prediction
    X_tr, X_te, y_tr, y_te, feats = split_data(df_enc, target="revenue")
    rev_results, best_rev = train_revenue_models(X_tr, X_te, y_tr, y_te, feats)

    # Churn prediction
    X_tr2, X_te2, y_tr2, y_te2, feats2 = split_data(df_enc, target="customer_churned")
    churn_results, best_churn = train_churn_models(X_tr2, X_te2, y_tr2, y_te2, feats2)
