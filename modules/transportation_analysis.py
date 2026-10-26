"""
ChainGuard AI - Transportation & Delivery Risk Intelligence Module
Analyzes carrier SLAs, transit lead-times, route-level delays,
modal cost distributions, and in-transit delivery bottlenecks.
"""

import pandas as pd
import numpy as np

def analyze_transportation_performance(trans_df, po_df=None):
    """
    Computes carrier reliability, transit lead times, delay distributions,
    and route-specific bottlenecks from historical shipment records.
    """
    if trans_df is None or trans_df.empty:
        return pd.DataFrame(), pd.DataFrame(), {}

    df = trans_df.copy()

    # Parse dates
    df["ship_dt"] = pd.to_datetime(df["shipment_date"], errors="coerce")
    df["est_arr_dt"] = pd.to_datetime(df["estimated_arrival_date"], errors="coerce")
    df["act_arr_dt"] = pd.to_datetime(df["actual_arrival_date"], errors="coerce")

    # Transit time and delay
    df["actual_transit_days"] = (df["act_arr_dt"] - df["ship_dt"]).dt.days
    df["delay_days"] = (df["act_arr_dt"] - df["est_arr_dt"]).dt.days

    # Route column (Origin -> Destination)
    df["route"] = df["origin"].astype(str) + " -> " + df["destination"].astype(str)

    # Identify completed vs in-transit
    completed = df[df["act_arr_dt"].notna()].copy()
    in_transit = df[df["act_arr_dt"].isna()].copy()

    # On-time is delay <= 0
    completed["is_on_time"] = completed["delay_days"] <= 0
    completed["is_delayed"] = completed["delay_days"] > 0

    # 1. Carrier Level Performance
    carrier_records = []
    for car_id in df["carrier_id"].dropna().unique():
        c_all = df[df["carrier_id"] == car_id]
        c_comp = completed[completed["carrier_id"] == car_id]
        
        tot_shipments = len(c_all)
        comp_count = len(c_comp)

        if comp_count > 0:
            otd_count = int(c_comp["is_on_time"].sum())
            otd_rate = round(otd_count / comp_count, 3)
            avg_transit = round(c_comp["actual_transit_days"].mean(), 1)
            transit_std = round(c_comp["actual_transit_days"].std(), 1) if comp_count > 1 else 0.0
            
            lates = c_comp[c_comp["delay_days"] > 0]
            avg_delay = round(lates["delay_days"].mean(), 1) if len(lates) > 0 else 0.0
            delay_std = round(lates["delay_days"].std(), 1) if len(lates) > 1 else 0.0
        else:
            otd_rate = 0.90
            avg_transit = 10.0
            transit_std = 0.0
            avg_delay = 0.0
            delay_std = 0.0

        # Transit modes used
        modes = ", ".join(c_all["transport_mode"].dropna().unique())
        tot_freight = round(c_all["shipping_cost"].sum(), 2)

        # Carrier SLA Reliability Score (0-100)
        reliability = round(otd_rate * 100.0 - min(30.0, avg_delay * 2.0), 1)
        reliability = max(10.0, min(100.0, reliability))

        carrier_records.append({
            "carrier_id": car_id,
            "total_shipments": tot_shipments,
            "completed_shipments": comp_count,
            "on_time_rate": otd_rate,
            "avg_transit_days": avg_transit,
            "transit_std_dev": transit_std,
            "avg_delay_days": avg_delay,
            "delay_std_dev": delay_std,
            "primary_modes": modes,
            "total_shipping_cost": tot_freight,
            "reliability_score": reliability,
            "risk_rating": "High Risk" if reliability < 70 else ("Moderate" if reliability < 85 else "Reliable")
        })

    df_carrier = pd.DataFrame(carrier_records)

    # 2. Route Level Performance (Origin -> Destination)
    route_records = []
    df["route"] = df["origin"].astype(str) + " ➔ " + df["destination"].astype(str)
    
    for route_name in df["route"].unique():
        r_all = df[df["route"] == route_name]
        r_comp = completed[completed["route"] == route_name]

        if len(r_comp) > 0:
            r_otd = round((r_comp["is_on_time"].sum() / len(r_comp)), 3)
            r_delay = round(r_comp[r_comp["delay_days"] > 0]["delay_days"].mean(), 1) if (r_comp["delay_days"] > 0).any() else 0.0
            r_transit = round(r_comp["actual_transit_days"].mean(), 1)
        else:
            r_otd = 0.90
            r_delay = 0.0
            r_transit = 12.0

        route_records.append({
            "route": route_name,
            "shipment_count": len(r_all),
            "on_time_rate": r_otd,
            "avg_transit_days": r_transit,
            "avg_delay_days": r_delay,
            "transport_mode": r_all["transport_mode"].iloc[0] if len(r_all) > 0 else "Unknown",
            "total_cost": round(r_all["shipping_cost"].sum(), 2)
        })

    df_route = pd.DataFrame(route_records).sort_values("shipment_count", ascending=False)

    # 3. Overall KPI Summary
    summary = {
        "total_shipments": len(df),
        "in_transit_count": len(in_transit),
        "overall_on_time_rate": round(completed["is_on_time"].mean(), 3) if len(completed) > 0 else 0.88,
        "avg_shipment_delay": round(completed[completed["delay_days"] > 0]["delay_days"].mean(), 1) if (completed["delay_days"] > 0).any() else 0.0,
        "total_freight_spend": round(df["shipping_cost"].sum(), 2),
        "delayed_in_transit": len(in_transit[in_transit["shipment_status"].astype(str).str.contains("Delayed", case=False, na=False)])
    }

    return df_carrier, df_route, summary
