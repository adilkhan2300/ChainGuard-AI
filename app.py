"""
ChainGuard AI — Supply Chain Risk Prediction & Resilience Intelligence Platform
Main Application Master Controller and Multi-Page Router.
"""

import streamlit as st
import os
import pandas as pd

# Configure page layout and aesthetics
st.set_page_config(
    page_title="ChainGuard AI — Supply Chain Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.ui_components import apply_custom_styles
from modules.data_loader import load_default_data

import importlib

# Dynamically import page modules with numbered filenames
page_exec = importlib.import_module("pages.1_Executive_Overview")
page_data = importlib.import_module("pages.2_Data_Upload_and_Validation")
page_sup = importlib.import_module("pages.3_Supplier_Risk_Intelligence")
page_inv = importlib.import_module("pages.4_Inventory_Intelligence")
page_prod = importlib.import_module("pages.5_Production_Risk_Analysis")
page_trans = importlib.import_module("pages.6_Transportation_Risk")
page_ml = importlib.import_module("pages.7_Disruption_Prediction")
page_alerts = importlib.import_module("pages.8_Risk_Alerts_and_Mitigation")
page_strat = importlib.import_module("pages.9_Strategy_Cost_Comparison")
page_sim = importlib.import_module("pages.10_Scenario_Simulator")
page_fin = importlib.import_module("pages.11_Financial_Impact")
page_rep = importlib.import_module("pages.12_Reports_and_Exports")
page_meth = importlib.import_module("pages.13_Methodology")

def main():
    apply_custom_styles()

    # Initialize Global Data Session State
    if "data_dict" not in st.session_state:
        st.session_state["data_dict"] = load_default_data()

    data_dict = st.session_state["data_dict"]

    # Sidebar Navigation & Global Filters
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 12px; margin-top: 5px;">
            <div style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #1e40af 0%, #4338ca 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🛡️ ChainGuard AI
            </div>
            <div style="font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">
                Supply Chain Risk & Resilience
            </div>
        </div>
        <hr style="border: 0; height: 1px; background: #e2e8f0; margin-bottom: 18px;" />
        """, unsafe_allow_html=True)

        # Page Selection Radio
        page_options = [
            "1. 📊 Executive Overview",
            "2. 📥 Data Upload & Validation",
            "3. 🏭 Supplier Risk Intelligence",
            "4. 📦 Inventory Intelligence",
            "5. ⚙️ Production Risk Analysis",
            "6. 🚢 Transportation Risk",
            "7. 🤖 Disruption Prediction (ML)",
            "8. 🚨 Risk Alerts & Mitigation",
            "9. ⚖️ Strategy Cost Comparison",
            "10. 🎛️ Scenario Simulator",
            "11. 💰 Financial Impact",
            "12. 📑 Reports & Exports",
            "13. 📘 Methodology & AI Governance"
        ]

        selected_page = st.radio(
            "Navigate Modules:",
            options=page_options,
            index=0
        )

        st.markdown("<hr style='border: 0; height: 1px; background: #e2e8f0; margin: 18px 0;' />", unsafe_allow_html=True)
        st.markdown("### 🌐 Global Operational Filters")

        # Global Plant Filter
        inv_df = data_dict.get("inventory")
        available_plants = ["All Facilities"]
        if inv_df is not None and not inv_df.empty and "plant_id" in inv_df.columns:
            available_plants += sorted(inv_df["plant_id"].dropna().unique().tolist())

        sel_plant = st.selectbox("Manufacturing Plant:", available_plants)
        plant_filter = None if sel_plant == "All Facilities" else [sel_plant]

        # Global Supplier Filter
        sups_df = data_dict.get("suppliers")
        available_sups = ["All Suppliers"]
        if sups_df is not None and not sups_df.empty and "supplier_id" in sups_df.columns:
            available_sups += sorted(sups_df["supplier_id"].dropna().unique().tolist())

        sel_sup = st.selectbox("Primary Supplier:", available_sups)
        sup_filter = None if sel_sup == "All Suppliers" else [sel_sup]

        global_filters = {
            "plant": plant_filter,
            "supplier": sup_filter
        }

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Quick Reload Data", use_container_width=True):
            st.session_state["data_dict"] = load_default_data()
            st.rerun()

        st.caption("ChainGuard AI v2.4 Enterprise | MBA Operations & AI Project")

    # Route to Selected Page
    if "Executive Overview" in selected_page:
        page_exec.render_page(data_dict, filters=global_filters)
    elif "Data Upload" in selected_page:
        page_data.render_page(data_dict)
    elif "Supplier Risk" in selected_page:
        page_sup.render_page(data_dict, filters=global_filters)
    elif "Inventory Intelligence" in selected_page:
        page_inv.render_page(data_dict, filters=global_filters)
    elif "Production Risk" in selected_page:
        page_prod.render_page(data_dict, filters=global_filters)
    elif "Transportation Risk" in selected_page:
        page_trans.render_page(data_dict, filters=global_filters)
    elif "Disruption Prediction" in selected_page:
        page_ml.render_page(data_dict, filters=global_filters)
    elif "Risk Alerts" in selected_page:
        page_alerts.render_page(data_dict, filters=global_filters)
    elif "Strategy Cost Comparison" in selected_page:
        page_strat.render_page(data_dict, filters=global_filters)
    elif "Scenario Simulator" in selected_page:
        page_sim.render_page(data_dict, filters=global_filters)
    elif "Financial Impact" in selected_page:
        page_fin.render_page(data_dict, filters=global_filters)
    elif "Reports & Exports" in selected_page:
        page_rep.render_page(data_dict, filters=global_filters)
    elif "Methodology" in selected_page:
        page_meth.render_page(data_dict, filters=global_filters)

if __name__ == "__main__":
    main()
