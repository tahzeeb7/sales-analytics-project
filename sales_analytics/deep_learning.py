"""
src/deep_learning.py
====================
LSTM & GRU models for time-series sales forecasting.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
    from tensorflow.keras.optimizers import Adam
    TF_AVAILABLE = True
except ImportError:
    print("TensorFlow not installed. Install with: pip install tensorflow")
    TF_AVAILABLE = False

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


# ─── DATA PREPARATION ────────────────────────────────────

def prepare_time_series(df: pd.DataFrame,
                         freq: str = "D",
                         target_col: str = "revenue",
                         look_back: int = 30) -> tuple:
    """
    Aggregate daily/weekly revenue, create sliding window sequences.
    Returns: (X_train, X_test, y_train, y_test, scaler, ts_series)
    """
    ts = df.resample(freq, on="date")[target_col].sum().reset_index()
    ts = ts.rename(columns={"date": "ds", target_col: "y"})
    ts = ts.sort_values("ds").reset_index(drop=True)

    # Normalize
    scaler = MinMaxScaler(feature_range=(0, 1))
    values = scaler.fit_transform(ts[["y"]].values)

    X, y = [], []
    for i in range(look_back, len(values)):
        X.append(values[i - look_back:i, 0])
        y.append(values[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    split = int(len(X) * 0.8)
    X_train, X_test   = X[:split], X[split:]
    y_train, y_test   = y[:split], y[split:]

    print(f"Time series: {len(ts)} {freq} data points | "
          f"look_back={look_back} | train={len(X_train)} test={len(X_test)}")
    return X_train, X_test, y_train, y_test, scaler, ts


# ─── MODEL BUILDERS ──────────────────────────────────────

def build_lstm_model(look_back: int, units: int = 128) -> "tf.keras.Model":
    model = Sequential([
        LSTM(units, return_sequences=True, input_shape=(look_back, 1)),
        Dropout(0.2),
        BatchNormalization(),
        LSTM(units // 2, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=1e-3), loss="mse", metrics=["mae"])
    model.summary()
    return model


def build_gru_model(look_back: int, units: int = 128) -> "tf.keras.Model":
    model = Sequential([
        GRU(units, return_sequences=True, input_shape=(look_back, 1)),
        Dropout(0.2),
        BatchNormalization(),
        GRU(units // 2, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=1e-3), loss="mse", metrics=["mae"])
    return model


# ─── TRAINING ────────────────────────────────────────────

def train_deep_model(model, X_train, y_train, X_test, y_test,
                      model_name: str = "lstm",
                      epochs: int = 100, batch_size: int = 32):
    if not TF_AVAILABLE:
        print("TensorFlow not available. Skipping deep learning training.")
        return None, None

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=7, min_lr=1e-6),
        ModelCheckpoint(f"{MODEL_DIR}/{model_name}_best.keras",
                        save_best_only=True, monitor="val_loss"),
    ]

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=1,
    )

    plot_training_history(history, model_name)
    return model, history


# ─── EVALUATION ──────────────────────────────────────────

def evaluate_deep_model(model, X_test, y_test, scaler, model_name: str = "lstm"):
    if model is None:
        return {}

    preds_scaled = model.predict(X_test, verbose=0)
    preds_inv    = scaler.inverse_transform(preds_scaled)
    actual_inv   = scaler.inverse_transform(y_test.reshape(-1, 1))

    mae  = mean_absolute_error(actual_inv, preds_inv)
    rmse = np.sqrt(mean_squared_error(actual_inv, preds_inv))
    r2   = r2_score(actual_inv, preds_inv)

    print(f"\n{model_name.upper()} Results:")
    print(f"  MAE:  {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R²:   {r2:.4f}")

    plot_forecast(actual_inv, preds_inv, model_name)
    return {"MAE": mae, "RMSE": rmse, "R2": r2,
            "actuals": actual_inv.flatten(), "preds": preds_inv.flatten()}


# ─── FUTURE FORECASTING ──────────────────────────────────

def forecast_future(model, last_sequence: np.ndarray,
                    scaler, n_steps: int = 30) -> np.ndarray:
    """Generate n_steps ahead forecast from the last known window."""
    if model is None:
        return np.zeros(n_steps)

    seq = last_sequence.copy()
    forecasts = []

    for _ in range(n_steps):
        inp = seq[-seq.shape[0]:].reshape(1, seq.shape[0], 1)
        pred = model.predict(inp, verbose=0)[0, 0]
        forecasts.append(pred)
        seq = np.append(seq[1:], [[pred]], axis=0)

    forecasts_inv = scaler.inverse_transform(np.array(forecasts).reshape(-1, 1))
    return forecasts_inv.flatten()


# ─── PLOTS ───────────────────────────────────────────────

def plot_training_history(history, name: str):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(history.history["loss"], label="Train Loss")
    axes[0].plot(history.history["val_loss"], label="Val Loss")
    axes[0].set_title(f"{name.upper()} — Training Loss")
    axes[0].legend()

    axes[1].plot(history.history["mae"], label="Train MAE")
    axes[1].plot(history.history["val_mae"], label="Val MAE")
    axes[1].set_title(f"{name.upper()} — MAE")
    axes[1].legend()

    plt.tight_layout()
    os.makedirs("reports", exist_ok=True)
    plt.savefig(f"reports/{name}_training.png", dpi=150)
    plt.close()


def plot_forecast(actuals, preds, name: str):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(actuals[:100], label="Actual", linewidth=2, color="#5B6AF0")
    ax.plot(preds[:100],   label="Predicted", linewidth=2,
            color="#F04E6A", linestyle="--")
    ax.set_title(f"{name.upper()} — Forecast vs Actual")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"reports/{name}_forecast.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    import sys
    sys.path.append("src")
    from preprocessing import load_data, engineer_features

    df  = load_data("data/sales_data.csv")
    df  = engineer_features(df)
    df["date"] = pd.to_datetime(df["date"])

    LOOK_BACK = 30

    X_tr, X_te, y_tr, y_te, scaler, ts = prepare_time_series(
        df, freq="W", look_back=LOOK_BACK
    )

    if TF_AVAILABLE:
        # LSTM
        lstm_model = build_lstm_model(LOOK_BACK)
        lstm_model, lstm_hist = train_deep_model(
            lstm_model, X_tr, y_tr, X_te, y_te, "lstm", epochs=80
        )
        lstm_results = evaluate_deep_model(lstm_model, X_te, y_te, scaler, "lstm")

        # GRU
        gru_model  = build_gru_model(LOOK_BACK)
        gru_model, gru_hist = train_deep_model(
            gru_model, X_tr, y_tr, X_te, y_te, "gru", epochs=80
        )
        gru_results = evaluate_deep_model(gru_model, X_te, y_te, scaler, "gru")

        # Future forecast
        last_seq = X_te[-1]
        future   = forecast_future(lstm_model, last_seq, scaler, n_steps=30)
        print(f"\n30-day forecast (LSTM): {future.round(2)}")
