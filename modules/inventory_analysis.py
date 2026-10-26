"""
ChainGuard AI - Inventory Intelligence & Stockout Prediction Module
Calculates Net Available Stock, Days of Coverage, Dynamic Safety Stock,
Reorder Points, Stockout Projections, and Inventory Valuation.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_inventory_metrics(inv_df, po_df=None, demand_df=None, service_level=0.95):
    """
    Computes core inventory KPIs and stockout indicators.
    Formulae:
      - Net Available Stock = Current Stock - Reserved Stock
      - Days of Coverage = Net Available Stock / Average Daily Demand (if Demand > 0)
      - Projected Stockout Date = Inventory Date + Days of Coverage
      - Safety Stock = z * sqrt(L * sigma_d^2 + D^2 * sigma_L^2)
    """
    if inv_df is None or inv_df.empty:
        return pd.DataFrame()

    df = inv_df.copy()

    # Numeric conversions
    numeric_cols = [
        "current_stock", "reserved_stock", "safety_stock",
        "reorder_point", "average_daily_demand", "inventory_unit_cost"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # 1. Net Available Stock
    df["net_available_stock"] = df["current_stock"] - df["reserved_stock"]
    # Handle negative net stock safely
    df["net_available_stock"] = df["net_available_stock"].clip(lower=0.0)

    # 2. Days of Coverage
    df["days_of_coverage"] = np.where(
        df["average_daily_demand"] > 0,
        (df["net_available_stock"] / df["average_daily_demand"]).round(1),
        999.0 # infinite or zero demand
    )

    # 3. Inventory Value
    df["inventory_value"] = (df["current_stock"] * df["inventory_unit_cost"]).round(2)

    # 4. Projected Stockout Date
    # Base date from dataset or default to today
    def get_stockout_date(row):
        inv_dt_str = str(row.get("inventory_date", ""))
        try:
            base_dt = pd.to_datetime(inv_dt_str)
        except Exception:
            base_dt = datetime.now()

        coverage = row["days_of_coverage"]
        if coverage >= 365 or coverage == 999.0:
            return "No Immediate Risk (>1 Yr)"
        try:
            target_dt = base_dt + timedelta(days=float(coverage))
            return target_dt.strftime("%Y-%m-%d")
        except Exception:
            return "N/A"

    df["projected_stockout_date"] = df.apply(get_stockout_date, axis=1)

    # 5. Incoming Open POs Quantities & Next Delivery Date
    incoming_qty_map = {}
    next_arrival_map = {}

    if po_df is not None and not po_df.empty:
        open_pos = po_df[po_df["actual_delivery_date"].isna() | (po_df["actual_delivery_date"] == "")].copy()
        if "promised_delivery_date" in open_pos.columns:
            open_pos["promised_dt"] = pd.to_datetime(open_pos["promised_delivery_date"], errors="coerce")
            for m_id in df["material_id"].unique():
                m_pos = open_pos[open_pos["material_id"] == m_id]
                incoming_qty_map[m_id] = int(m_pos["quantity_ordered"].sum())
                valid_dates = m_pos["promised_dt"].dropna().sort_values()
                if not valid_dates.empty:
                    next_arrival_map[m_id] = valid_dates.iloc[0].strftime("%Y-%m-%d")
                else:
                    next_arrival_map[m_id] = "No Open PO"
    
    df["incoming_po_quantity"] = df["material_id"].map(incoming_qty_map).fillna(0).astype(int)
    df["next_replenishment_date"] = df["material_id"].map(next_arrival_map).fillna("No Open PO")

    # 6. Status and Stockout Risk Classification
    # Critical: Coverage < 5 days or Net Available < 0.3 * Safety Stock
    # At Risk / Below ROP: Current Stock < Reorder Point
    # Overstocked: Coverage > 60 days and Current Stock > 3 * ROP
    # Healthy: Balanced
    conditions = [
        (df["days_of_coverage"] < 7.0) | (df["net_available_stock"] < df["safety_stock"] * 0.4),
        (df["current_stock"] < df["reorder_point"]) | (df["net_available_stock"] < df["safety_stock"]),
        (df["days_of_coverage"] > 60.0) & (df["current_stock"] > df["reorder_point"] * 2.5)
    ]
    choices = ["Critical Stockout Risk", "Below Reorder Point", "Overstocked / Excess"]
    df["inventory_status"] = np.select(conditions, choices, default="Optimal / Healthy")

    # Severity Level for filtering
    severity_map = {
        "Critical Stockout Risk": "Critical",
        "Below Reorder Point": "High",
        "Overstocked / Excess": "Low",
        "Optimal / Healthy": "Optimal"
    }
    df["risk_severity"] = df["inventory_status"].map(severity_map)

    return df

def calculate_theoretical_safety_stock(avg_demand, demand_std, lead_time_days, lt_std=0.0, service_level=0.95):
    """
    Computes safety stock using statistical formula:
    SS = z * sqrt(L * sigma_D^2 + D^2 * sigma_L^2)
    where z is the standard normal quantile for service_level.
    """
    z_scores = {0.90: 1.28, 0.95: 1.645, 0.975: 1.96, 0.99: 2.33}
    z = z_scores.get(service_level, 1.645)
    
    var_component = (lead_time_days * (demand_std ** 2)) + ((avg_demand ** 2) * (lt_std ** 2))
    ss = z * np.sqrt(max(0.0, var_component))
    return int(round(ss))
