"""
ChainGuard AI - Page 6: Transportation and Delivery Risk Intelligence
Monitors carrier performance SLAs, route-level transit delays,
modal freight spend distributions, and in-transit delivery bottlenecks.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.ui_components import (
    apply_custom_styles, render_header, render_alert,
    get_plotly_theme, get_badge
)
from modules.transportation_analysis import analyze_transportation_performance

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Transportation & Logistics Risk Intelligence",
        subtitle="Empirical carrier SLA tracking, corridor transit lead-times, and in-transit bottleneck detection"
    )

    trans_df = data_dict.get("transportation", pd.DataFrame())
    po_df = data_dict.get("purchase_orders", pd.DataFrame())

    if trans_df.empty:
        st.warning("No transportation records available. Please upload transportation.csv or reset demo data.")
        return

    # Compute logistics analytics
    df_carrier, df_route, summary = analyze_transportation_performance(trans_df, po_df)

    # 1. Summary Alert Banner
    delayed_in_transit = summary.get("delayed_in_transit", 0)
    avg_delay = summary.get("avg_shipment_delay", 0)

    render_alert(
        f"<strong>LOGISTICS DISRUPTION ALERT:</strong> <strong>{delayed_in_transit} Inbound Shipments</strong> are currently delayed in transit. "
        f"Average delay across delayed shipments is <strong>{avg_delay:.1f} days</strong>. Primary corridor delays observed along "
        f"Trans-Eurasia Rail and Trans-Pacific Ocean routes.",
        alert_type="warning" if delayed_in_transit > 0 else "info"
    )

    # 2. Executive KPI Cards
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.metric("Total Shipments Tracked", f"{summary.get('total_shipments', 0)} Cargoes", delta="Multimodal Network")
    with t2:
        otd = round(summary.get("overall_on_time_rate", 0.9) * 100, 1)
        st.metric("Network On-Time Delivery", f"{otd}%", delta="Target SLA >= 92%", delta_color="normal" if otd >= 92 else "inverse")
    with t3:
        st.metric("Active In-Transit Shipments", f"{summary.get('in_transit_count', 0)} Shipments", delta=f"{delayed_in_transit} Delayed", delta_color="inverse")
    with t4:
        tot_spend = summary.get("total_freight_spend", 0)
        st.metric("Total Freight Spend", f"${tot_spend:,.2f}", delta="Air, Ocean, Road, Rail")

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 20px 0;' />", unsafe_allow_html=True)

    # 3. Carrier SLA Reliability Scorecard
    st.markdown("### 🚢 Carrier SLA Performance & Reliability Scorecard")
    st.dataframe(
        df_carrier.sort_values("reliability_score", ascending=True),
        column_config={
            "on_time_rate": st.column_config.ProgressColumn("On-Time Rate", min_value=0, max_value=1, format="%.1f"),
            "reliability_score": st.column_config.NumberColumn("Reliability Score (0-100)", format="%.1f"),
            "total_shipping_cost": st.column_config.NumberColumn("Total Freight Spend", format="$%.2f")
        },
        use_container_width=True,
        height=260
    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 4. Visual Diagnostics
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("#### Carrier Reliability vs Average Transit Days")
        fig_car = px.scatter(
            df_carrier,
            x="avg_transit_days",
            y="on_time_rate",
            size="total_shipments",
            color="risk_rating",
            hover_name="carrier_id",
            hover_data={"primary_modes": True, "avg_delay_days": True},
            color_discrete_map={
                "High Risk": "#ef4444",
                "Moderate": "#f59e0b",
                "Reliable": "#10b981"
            },
            labels={"avg_transit_days": "Avg Transit Time (Days)", "on_time_rate": "On-Time Rate (0-1.0)"}
        )
        fig_car.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_car, use_container_width=True)

    with c_right:
        st.markdown("#### Freight Spend Distribution by Transport Mode")
        mode_spend = trans_df.groupby("transport_mode")["shipping_cost"].sum().reset_index()
        fig_mode = px.pie(
            mode_spend,
            values="shipping_cost",
            names="transport_mode",
            hole=0.45,
            color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]
        )
        fig_mode.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_mode, use_container_width=True)

    # 5. Route-Level Delay Patterns & In-Transit Watchlist
    st.markdown("### 🗺️ Transit Corridor Route Performance")
    st.dataframe(
        df_route.head(10),
        column_config={
            "on_time_rate": st.column_config.ProgressColumn("On-Time Rate", min_value=0, max_value=1, format="%.1f"),
            "total_cost": st.column_config.NumberColumn("Total Freight ($)", format="$%.2f")
        },
        use_container_width=True
    )

    # Governance Notice
    st.markdown("""
    <div style="background: #f1f5f9; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #475569; border: 1px solid #e2e8f0; margin-top: 20px;">
        <strong>Methodological Clarity:</strong> Transportation metrics are calculated from recorded bill-of-lading and shipment timestamps. 
        The system does not claim real-time IoT or GPS satellite vessel monitoring.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
