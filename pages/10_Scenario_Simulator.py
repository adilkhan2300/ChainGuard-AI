"""
ChainGuard AI - Page 10: Supply Chain Scenario Simulator
Interactive what-if simulator modeling supplier lead time shifts, demand shocks,
safety stock buffer modifications, and emergency expediting interventions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.ui_components import (
    apply_custom_styles, render_header, render_alert,
    get_plotly_theme
)
from modules.inventory_analysis import calculate_inventory_metrics
from modules.production_risk import evaluate_production_material_risk
from modules.supplier_risk import calculate_supplier_metrics
from modules.scenario_simulator import simulate_supply_chain_scenario

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Interactive Supply Chain Scenario Simulator",
        subtitle="Model systemic operational shocks and stress-test inventory, production, and financial resilience"
    )

    inv_df = data_dict.get("inventory", pd.DataFrame())
    pos_df = data_dict.get("purchase_orders", pd.DataFrame())
    prod_df = data_dict.get("production", pd.DataFrame())
    bom_df = data_dict.get("bill_of_materials", pd.DataFrame())
    sups_df = data_dict.get("suppliers", pd.DataFrame())

    if inv_df.empty:
        st.warning("Insufficient baseline data to run scenario simulations.")
        return

    # Baseline calculations
    base_inv = calculate_inventory_metrics(inv_df, pos_df)
    base_prod, _ = evaluate_production_material_risk(prod_df, bom_df, base_inv, pos_df)
    base_sups = calculate_supplier_metrics(sups_df, pos_df, bom_df)

    # 1. Interactive Shock Control Sliders
    st.markdown("### 🎛️ Simulation Shock Controls")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        lead_time_shock = st.slider("Supplier Lead Time Shift (Days):", -10, 30, 8, help="Simulates vendor port congestion or raw material delays.")
        demand_surge = st.slider("Demand Volatility Surge (%):", -30, 60, 20, help="Simulates unforecasted customer order spikes.")
    with col2:
        ss_mult = st.slider("Safety Stock Policy Multiplier:", 0.5, 2.5, 1.2, 0.1, help="Simulates corporate mandate to raise or lower working capital buffers.")
        trans_delay = st.slider("Corridor Transportation Delay (Days):", 0, 20, 5, help="Simulates customs hold-ups or carrier bottlenecks.")
    with col3:
        st.markdown("**Emergency Mitigation Interventions:**")
        act_expedite = st.toggle("🚀 Activate Dedicated Air Expediting", value=True, help="Absorbs 5 days of transit delay at a fixed logistics premium.")
        alt_alloc = st.slider("Secondary Supplier Volume Allocation (%):", 0, 50, 25, step=5, help="Shifts order volume to pre-qualified secondary vendors.")

    # Run Simulation
    comparison, sim_inv, sim_prod = simulate_supply_chain_scenario(
        base_inv_df=base_inv,
        base_prod_df=base_prod,
        base_sup_df=base_sups,
        lead_time_shock_days=lead_time_shock,
        demand_surge_pct=demand_surge,
        safety_stock_mult=ss_mult,
        transport_delay_days=trans_delay,
        activate_expediting=act_expedite
    )

    deltas = comparison["deltas"]
    base_m = comparison["baseline"]
    sim_m = comparison["scenario"]

    # 2. Simulation Outcome Summary Banner
    cost_diff = deltas["cost_diff"]
    cost_sign = "+" if cost_diff > 0 else ""
    render_alert(
        f"<strong>SIMULATION OUTCOME:</strong> Under this stress scenario, critical stockouts shift from "
        f"<strong>{base_m['critical_stockouts']} to {sim_m['critical_stockouts']} SKUs</strong> "
        f"({deltas['critical_stockouts_diff']:+d}). Average inventory coverage moves to <strong>{sim_m['avg_coverage_days']} days</strong> "
        f"({deltas['avg_coverage_days_diff']:+.1f}d). Total financial disruption exposure is estimated at "
        f"<strong>${sim_m['estimated_disruption_cost']:,.2f}</strong> ({cost_sign}${cost_diff:,.2f} vs baseline).",
        alert_type="warning" if cost_diff > 0 else "success",
        title="Simulated Stress Test Diagnostics"
    )

    # 3. Side-by-Side Comparison Metrics
    st.markdown("### 📊 Baseline vs Simulated Scenario Delta Comparison")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(
            "Critical Stockouts",
            f"{sim_m['critical_stockouts']} SKUs",
            delta=f"{deltas['critical_stockouts_diff']:+d} SKUs",
            delta_color="inverse"
        )
    with m2:
        st.metric(
            "Items Below ROP",
            f"{sim_m['items_below_rop']} SKUs",
            delta=f"{deltas['items_below_rop_diff']:+d} SKUs",
            delta_color="inverse"
        )
    with m3:
        st.metric(
            "Avg Coverage Days",
            f"{sim_m['avg_coverage_days']} Days",
            delta=f"{deltas['avg_coverage_days_diff']:+.1f} Days",
            delta_color="normal"
        )
    with m4:
        st.metric(
            "Production Orders at Risk",
            f"{sim_m['production_orders_at_risk']} Orders",
            delta=f"{deltas['production_orders_at_risk_diff']:+d} Orders",
            delta_color="inverse"
        )
    with m5:
        st.metric(
            "Disruption Exposure Cost",
            f"${sim_m['estimated_disruption_cost']:,.0f}",
            delta=f"{cost_sign}${cost_diff:,.0f}",
            delta_color="inverse"
        )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 4. Visual Diagnostics: Side-by-Side Bar Charts
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("#### Inventory Status Distribution: Baseline vs Scenario")
        base_counts = base_inv["inventory_status"].value_counts().reset_index()
        base_counts.columns = ["Status", "Count"]
        base_counts["Run"] = "Baseline"

        sim_counts = sim_inv["sim_status"].value_counts().reset_index()
        sim_counts.columns = ["Status", "Count"]
        sim_counts["Run"] = "Simulated Scenario"

        merged_counts = pd.concat([base_counts, sim_counts])
        fig_dist = px.bar(
            merged_counts,
            x="Status",
            y="Count",
            color="Run",
            barmode="group",
            color_discrete_sequence=["#3b82f6", "#f59e0b"]
        )
        fig_dist.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_v2:
        st.markdown("#### Financial Exposure Comparison ($)")
        comp_cost_df = pd.DataFrame([
            {"Environment": "Baseline", "Financial Exposure ($)": base_m["estimated_disruption_cost"]},
            {"Environment": "Simulated Scenario", "Financial Exposure ($)": sim_m["estimated_disruption_cost"]}
        ])
        fig_cost_comp = px.bar(
            comp_cost_df,
            x="Environment",
            y="Financial Exposure ($)",
            color="Environment",
            text_auto="$,.0f",
            color_discrete_sequence=["#3b82f6", "#ef4444" if cost_diff > 0 else "#10b981"]
        )
        fig_cost_comp.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_cost_comp, use_container_width=True)

    # 5. Simulated Vulnerable Material List
    st.markdown("### 🔍 Simulated High-Risk Materials Under Scenario Shock")
    sim_vulnerable = sim_inv[sim_inv["sim_status"] == "Critical Stockout Risk"][
        ["material_id", "material_name", "plant_id", "sim_avg_daily_demand", "sim_days_of_coverage", "sim_reorder_point"]
    ].sort_values("sim_days_of_coverage", ascending=True)
    st.dataframe(sim_vulnerable.head(10), use_container_width=True)

    # Governance Notice
    st.markdown("""
    <div style="background: #f1f5f9; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #475569; border: 1px solid #e2e8f0; margin-top: 20px;">
        <strong>Methodological Clarity:</strong> All simulated outcomes are hypothetical sensitivity projections designed for managerial stress-testing. 
        Simulations do not guarantee prevention of external force majeure disruptions.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
