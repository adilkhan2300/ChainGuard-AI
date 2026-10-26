"""
ChainGuard AI - Demand Forecasting & Volatility Analysis Module
Analyzes historical demand patterns, detects volatility spikes,
and generates forward projections using statsmodels and Scikit-learn.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_demand_series(demand_df, target_product=None):
    """
    Summarizes demand metrics, trend, coefficient of variation, and spike anomalies.
    """
    if demand_df is None or demand_df.empty:
        return {}

    df = demand_df.copy()
    if target_product and "product_id" in df.columns:
        df = df[df["product_id"] == target_product]

    if df.empty:
        return {}

    df["dt"] = pd.to_datetime(df["forecast_date"], errors="coerce")
    df = df.sort_values("dt").dropna(subset=["dt"])

    actuals = df["actual_demand"].values
    forecasts = df["forecast_quantity"].values

    mean_demand = np.mean(actuals)
    std_demand = np.std(actuals)
    cov = (std_demand / mean_demand) if mean_demand > 0 else 0.0

    # Accuracy metrics
    mae = np.mean(np.abs(actuals - forecasts))
    rmse = np.sqrt(np.mean((actuals - forecasts) ** 2))
    mape = np.mean(np.abs((actuals - forecasts) / np.maximum(actuals, 1))) * 100.0

    # Anomaly spike detection (z-score > 2.0)
    residuals = actuals - forecasts
    res_std = np.std(residuals)
    z_scores = np.abs(residuals) / (res_std if res_std > 0 else 1.0)
    spikes = df[z_scores > 2.0]

    return {
        "df_sorted": df,
        "mean_demand": round(float(mean_demand), 1),
        "std_demand": round(float(std_demand), 2),
        "coefficient_of_variation": round(float(cov), 3),
        "mae": round(float(mae), 2),
        "rmse": round(float(rmse), 2),
        "mape_percent": round(float(mape), 1),
        "spike_count": len(spikes),
        "spikes_df": spikes
    }

def generate_forward_forecast(demand_df, product_id, periods_ahead=8):
    """
    Produces forward demand forecasts using Holt's Linear Exponential Smoothing
    with fallback to linear trend if statsmodels fails.
    """
    if demand_df is None or demand_df.empty:
        return pd.DataFrame()

    df = demand_df[demand_df["product_id"] == product_id].copy()
    if len(df) < 4:
        return pd.DataFrame()

    df["dt"] = pd.to_datetime(df["forecast_date"], errors="coerce")
    df = df.sort_values("dt").dropna(subset=["dt"])

    y = df["actual_demand"].values
    last_date = df["dt"].iloc[-1]

    # Attempt statsmodels ExponentialSmoothing
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        model = ExponentialSmoothing(y, trend="add", seasonal=None, initialization_method="estimated")
        fit_model = model.fit()
        forecast_vals = fit_model.forecast(periods_ahead)
    except Exception:
        # Fallback to linear regression trend
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        future_x = np.arange(len(y), len(y) + periods_ahead)
        forecast_vals = intercept + slope * future_x

    forecast_vals = np.maximum(forecast_vals, 0.0).round().astype(int)

    future_dates = [last_date + timedelta(weeks=i + 1) for i in range(periods_ahead)]
    df_future = pd.DataFrame({
        "forecast_date": [d.strftime("%Y-%m-%d") for d in future_dates],
        "projected_demand": forecast_vals,
        "lower_bound_95": np.maximum(0, forecast_vals - (1.96 * np.std(y) * 0.5)).round().astype(int),
        "upper_bound_95": (forecast_vals + (1.96 * np.std(y) * 0.5)).round().astype(int)
    })
    return df_future
