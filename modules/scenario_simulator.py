"""
ChainGuard AI - Supply Chain Scenario Simulator Module
Runs interactive what-if simulations: supplier lead time shifts, demand shocks,
safety stock buffer modifications, and carrier delay fluctuations.
Compares baseline vs simulated metrics side-by-side.
"""

import pandas as pd
import numpy as np

def simulate_supply_chain_scenario(
    base_inv_df,
    base_prod_df,
    base_sup_df,
    lead_time_shock_days=0,
    demand_surge_pct=0.0,
    safety_stock_mult=1.0,
    transport_delay_days=0,
    activate_expediting=False
):
    """
    Computes hypothetical supply chain outcomes under dynamic operational shocks.
    Returns:
      - Comparison summary dictionary (Baseline vs Scenario)
      - Detailed simulated inventory DataFrame
      - Detailed simulated production DataFrame
    """
    if base_inv_df is None or base_inv_df.empty:
        return {}, pd.DataFrame(), pd.DataFrame()

    sim_inv = base_inv_df.copy()

    # 1. Apply Demand Surge
    demand_factor = 1.0 + (demand_surge_pct / 100.0)
    sim_inv["sim_avg_daily_demand"] = (sim_inv["average_daily_demand"] * demand_factor).round(1)

    # 2. Adjust Safety Stock Buffer
    sim_inv["sim_safety_stock"] = (sim_inv["safety_stock"] * safety_stock_mult).round().astype(int)

    # 3. Adjust Reorder Point based on lead time shock and demand surge
    lt_shock = lead_time_shock_days + (transport_delay_days if not activate_expediting else max(0, transport_delay_days - 5))
    sim_inv["sim_reorder_point"] = (
        (sim_inv["sim_avg_daily_demand"] * (20 + lt_shock)) + sim_inv["sim_safety_stock"]
    ).round().astype(int)

    # 4. Recalculate Net Stock & Days of Coverage
    net_stock = (sim_inv["current_stock"] - sim_inv["reserved_stock"]).clip(lower=0.0)
    sim_inv["sim_days_of_coverage"] = np.where(
        sim_inv["sim_avg_daily_demand"] > 0,
        (net_stock / sim_inv["sim_avg_daily_demand"]).round(1),
        999.0
    )

    # 5. Classify Scenario Inventory Risk
    sim_crit_mask = (sim_inv["sim_days_of_coverage"] < 7.0) | (net_stock < sim_inv["sim_safety_stock"] * 0.4)
    sim_below_rop_mask = (sim_inv["current_stock"] < sim_inv["sim_reorder_point"]) & (~sim_crit_mask)
    
    sim_inv["sim_status"] = np.select(
        [sim_crit_mask, sim_below_rop_mask],
        ["Critical Stockout Risk", "Below Reorder Point"],
        default="Optimal / Healthy"
    )

    # Baseline metrics
    base_crit_count = int((base_inv_df["risk_severity"] == "Critical").sum()) if "risk_severity" in base_inv_df.columns else 0
    base_below_rop = int((base_inv_df["inventory_status"] == "Below Reorder Point").sum()) if "inventory_status" in base_inv_df.columns else 0
    base_avg_coverage = round(float(base_inv_df["days_of_coverage"].replace(999.0, np.nan).dropna().mean()), 1)

    # Simulated metrics
    sim_crit_count = int(sim_crit_mask.sum())
    sim_below_rop = int(sim_below_rop_mask.sum())
    sim_avg_coverage = round(float(sim_inv["sim_days_of_coverage"].replace(999.0, np.nan).dropna().mean()), 1)

    # Production orders impact
    sim_prod = base_prod_df.copy() if base_prod_df is not None and not base_prod_df.empty else pd.DataFrame()
    if not sim_prod.empty:
        # Increase delay days if lead time shock positive and no expediting
        extra_delay = max(0, lt_shock)
        sim_prod["sim_potential_delay_days"] = sim_prod["potential_delay_days"] + (0 if activate_expediting else extra_delay)
        sim_prod_at_risk = int((sim_prod["sim_potential_delay_days"] > 0).sum())
        base_prod_at_risk = int((sim_prod["potential_delay_days"] > 0).sum())
    else:
        sim_prod_at_risk = 0
        base_prod_at_risk = 0

    # Financial Exposure Impact
    expediting_premium = 12500.0 if activate_expediting else 0.0
    sim_disruption_cost = (sim_crit_count * 15000.0) + (sim_prod_at_risk * 7500.0) + expediting_premium
    base_disruption_cost = (base_crit_count * 15000.0) + (base_prod_at_risk * 7500.0)

    comparison = {
        "baseline": {
            "critical_stockouts": base_crit_count,
            "items_below_rop": base_below_rop,
            "avg_coverage_days": base_avg_coverage,
            "production_orders_at_risk": base_prod_at_risk,
            "estimated_disruption_cost": base_disruption_cost
        },
        "scenario": {
            "critical_stockouts": sim_crit_count,
            "items_below_rop": sim_below_rop,
            "avg_coverage_days": sim_avg_coverage,
            "production_orders_at_risk": sim_prod_at_risk,
            "estimated_disruption_cost": sim_disruption_cost
        },
        "deltas": {
            "critical_stockouts_diff": sim_crit_count - base_crit_count,
            "items_below_rop_diff": sim_below_rop - base_below_rop,
            "avg_coverage_days_diff": round(sim_avg_coverage - base_avg_coverage, 1),
            "production_orders_at_risk_diff": sim_prod_at_risk - base_prod_at_risk,
            "cost_diff": round(sim_disruption_cost - base_disruption_cost, 2)
        }
    }

    return comparison, sim_inv, sim_prod
