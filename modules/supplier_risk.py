"""
ChainGuard AI - Supplier Risk Intelligence Module
Evaluates supplier reliability, lead-time variance, on-time delivery rates,
fulfillment shortfalls, single-source dependencies, and composite risk scoring.
"""

import pandas as pd
import numpy as np

def calculate_supplier_metrics(suppliers_df, po_df, bom_df=None):
    """
    Computes empirical supplier performance metrics from historical purchase order data.
    """
    if suppliers_df is None or suppliers_df.empty:
        return pd.DataFrame()

    sup_df = suppliers_df.copy()
    
    # Defaults if PO data is absent
    if po_df is None or po_df.empty:
        sup_df["total_pos"] = 0
        sup_df["completed_pos"] = 0
        sup_df["on_time_pos"] = 0
        sup_df["delayed_pos"] = 0
        sup_df["on_time_delivery_rate"] = np.nan
        sup_df["avg_delay_days"] = 0.0
        sup_df["avg_actual_lead_time"] = sup_df.get("contractual_lead_time_days", 30)
        sup_df["lead_time_std_dev"] = 0.0
        sup_df["fulfillment_rate"] = 1.0
        sup_df["total_qty_ordered"] = 0
        sup_df["total_qty_received"] = 0
        sup_df["is_single_source"] = False
        sup_df["single_source_materials"] = 0
        sup_df["supplier_risk_score"] = 25.0
        sup_df["risk_level"] = "Low"
        return sup_df

    # Parse dates in POs
    pos = po_df.copy()
    pos["order_dt"] = pd.to_datetime(pos["order_date"], errors="coerce")
    pos["promised_dt"] = pd.to_datetime(pos["promised_delivery_date"], errors="coerce")
    pos["actual_dt"] = pd.to_datetime(pos["actual_delivery_date"], errors="coerce")

    # Lead time in days
    pos["actual_lead_time"] = (pos["actual_dt"] - pos["order_dt"]).dt.days
    # Delay days (positive = late, negative = early)
    pos["delay_days"] = (pos["actual_dt"] - pos["promised_dt"]).dt.days

    # Identify single-source dependencies from BOM
    single_source_map = {}
    if bom_df is not None and not bom_df.empty and "approved_alternative_material" in bom_df.columns:
        # Materials without approved alternatives
        no_alt_mats = set(bom_df[bom_df["approved_alternative_material"].isna() | (bom_df["approved_alternative_material"] == "None")]["material_id"].unique())
        # Map suppliers to these materials
        for sup_id in sup_df["supplier_id"].unique():
            sup_mats = pos[pos["supplier_id"] == sup_id]["material_id"].unique()
            overlap = set(sup_mats).intersection(no_alt_mats)
            single_source_map[sup_id] = len(overlap)
    else:
        for sup_id in sup_df["supplier_id"].unique():
            single_source_map[sup_id] = 0

    metrics_list = []

    for _, s_row in sup_df.iterrows():
        sup_id = s_row["supplier_id"]
        s_pos = pos[pos["supplier_id"] == sup_id]

        total_orders = len(s_pos)
        # Completed orders are those with actual_dt or delivered statuses
        completed = s_pos[s_pos["actual_dt"].notna()]
        completed_count = len(completed)

        if completed_count > 0:
            # On-time is delayed <= 0 days
            on_time_count = len(completed[completed["delay_days"] <= 0])
            delayed_count = completed_count - on_time_count
            otd_rate = round(on_time_count / completed_count, 3)
            
            # Positive delays only for avg delay calculation
            lates = completed[completed["delay_days"] > 0]
            avg_delay = round(lates["delay_days"].mean(), 1) if len(lates) > 0 else 0.0
            
            avg_actual_lt = round(completed["actual_lead_time"].mean(), 1)
            lt_std = round(completed["actual_lead_time"].std(), 2) if completed_count > 1 else 0.0
            if pd.isna(lt_std):
                lt_std = 0.0

            tot_ordered = s_pos["quantity_ordered"].sum()
            tot_received = completed["quantity_received"].sum()
            fulfill_rate = round(tot_received / max(tot_ordered, 1), 3) if tot_ordered > 0 else 1.0
        else:
            # No completed records yet
            contract_lt = s_row.get("contractual_lead_time_days", 30)
            on_time_count = 0
            delayed_count = 0
            otd_rate = 0.90 # baseline assumed
            avg_delay = 0.0
            avg_actual_lt = float(contract_lt)
            lt_std = 2.0
            tot_ordered = s_pos["quantity_ordered"].sum() if total_orders > 0 else 0
            tot_received = 0
            fulfill_rate = 1.0

        # Open delayed orders
        open_pos = s_pos[s_pos["actual_dt"].isna()]
        open_delayed = len(open_pos[open_pos["purchase_order_status"].astype(str).str.contains("Delayed", case=False, na=False)])

        # Single source count
        ss_count = single_source_map.get(sup_id, 0)

        # Quality rating (1 to 5)
        quality = float(s_row.get("quality_rating", 4.0)) if pd.notna(s_row.get("quality_rating")) else 4.0
        # Financial risk (0 to 1)
        fin_risk = float(s_row.get("financial_risk_score", 0.15)) if pd.notna(s_row.get("financial_risk_score")) else 0.15

        metrics_list.append({
            "supplier_id": sup_id,
            "total_pos": total_orders,
            "completed_pos": completed_count,
            "on_time_pos": on_time_count,
            "delayed_pos": delayed_count,
            "open_delayed_pos": open_delayed,
            "on_time_delivery_rate": otd_rate,
            "avg_delay_days": avg_delay,
            "avg_actual_lead_time": avg_actual_lt,
            "lead_time_std_dev": lt_std,
            "fulfillment_rate": fulfill_rate,
            "total_qty_ordered": tot_ordered,
            "total_qty_received": tot_received,
            "quality_rating": quality,
            "financial_risk_score": fin_risk,
            "single_source_materials": ss_count,
            "is_single_source": ss_count > 0
        })

    df_metrics = pd.DataFrame(metrics_list)
    merged = pd.merge(sup_df, df_metrics, on="supplier_id", suffixes=("", "_calc"))
    
    # Calculate composite risk score
    merged = calculate_composite_supplier_score(merged)
    return merged

def calculate_composite_supplier_score(df, weights=None):
    """
    Computes a transparent, weighted supplier risk score (0-100) using 6 components:
    1. Delivery Unreliability (1 - OTD)
    2. Lead-Time Variability (Std Dev normalized)
    3. Fulfillment Shortfall (1 - Fulfillment Rate)
    4. Quality Defect Score (5 - Quality Rating) / 4
    5. Financial Risk Score
    6. Single-Source Dependency Exposure
    """
    if weights is None:
        weights = {
            "otd": 0.25,
            "lt_variability": 0.20,
            "fulfillment": 0.15,
            "quality": 0.15,
            "financial": 0.15,
            "single_source": 0.10
        }

    scores = []
    levels = []

    for _, row in df.iterrows():
        otd = row.get("on_time_delivery_rate", 0.9)
        if pd.isna(otd):
            otd = 0.90
        otd_risk = (1.0 - otd) * 100.0

        lt_std = row.get("lead_time_std_dev", 0.0)
        # 10 days std dev represents high variability
        lt_var_risk = min(1.0, lt_std / 10.0) * 100.0

        fulfill = row.get("fulfillment_rate", 1.0)
        if pd.isna(fulfill):
            fulfill = 1.0
        fulfill_risk = (1.0 - fulfill) * 100.0

        quality = row.get("quality_rating", 4.0)
        # Scale 1-5 to 0-100 risk (5 stars = 0 risk, 1 star = 100 risk)
        quality_risk = max(0.0, min(100.0, ((5.0 - quality) / 4.0) * 100.0))

        fin = row.get("financial_risk_score", 0.15)
        fin_risk = min(100.0, max(0.0, fin * 100.0))

        ss_count = row.get("single_source_materials", 0)
        ss_risk = min(100.0, ss_count * 35.0)

        # Weighted calculation
        composite = (
            weights["otd"] * otd_risk +
            weights["lt_variability"] * lt_var_risk +
            weights["fulfillment"] * fulfill_risk +
            weights["quality"] * quality_risk +
            weights["financial"] * fin_risk +
            weights["single_source"] * ss_risk
        )
        composite = round(min(100.0, max(0.0, composite)), 1)
        scores.append(composite)

        # Level classification
        if composite >= 70.0:
            levels.append("Critical")
        elif composite >= 50.0:
            levels.append("Elevated Risk")
        elif composite >= 30.0:
            levels.append("Moderate")
        else:
            levels.append("Low Risk")

    df["supplier_risk_score"] = scores
    df["risk_level"] = levels
    return df
