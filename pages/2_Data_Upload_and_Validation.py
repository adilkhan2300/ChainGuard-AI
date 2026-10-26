"""
ChainGuard AI - Page 2: Data Integration & Upload Management
Allows independent uploads of CSV/Excel files, automatic column mapping,
schema validation, date parsing, referential integrity checks, and downloadable templates.
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.ui_components import apply_custom_styles, render_header, render_alert
from modules.data_loader import (
    DATASET_SCHEMAS, load_file, generate_csv_template,
    generate_all_templates_excel, load_default_data
)
from modules.data_validation import (
    validate_dataset, check_referential_integrity,
    assess_analytical_feasibility
)

def render_page(data_dict, on_data_update=None):
    apply_custom_styles()
    render_header(
        title="Data Integration & Validation Hub",
        subtitle="Manage CSV/Excel datasets, verify relational integrity, and inspect schema diagnostics"
    )

    # 1. Downloadable Templates Section
    st.markdown("### 📥 Downloadable Data Templates")
    st.write("Ensure your files match expected schema headers before uploading. Download pre-formatted sample templates below:")

    t_col1, t_col2 = st.columns([1, 2])
    with t_col1:
        excel_data = generate_all_templates_excel()
        st.download_button(
            label="📊 Download Master Excel Template (.xlsx)",
            data=excel_data,
            file_name="ChainGuard_Master_Templates.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with t_col2:
        with st.expander("📄 Download Individual CSV Templates with Sample Rows"):
            csv_cols = st.columns(4)
            for idx, ds_name in enumerate(DATASET_SCHEMAS.keys()):
                col = csv_cols[idx % 4]
                with col:
                    csv_bytes = generate_csv_template(ds_name)
                    st.download_button(
                        label=f"{ds_name}.csv",
                        data=csv_bytes,
                        file_name=f"{ds_name}_template.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 20px 0;' />", unsafe_allow_html=True)

    # 2. File Upload & Dataset Management
    st.markdown("### 📤 Upload Enterprise Data Files")
    st.write("Upload individual CSV or Excel files. Files will be automatically mapped, cleaned, and validated against referential integrity constraints.")

    # Reset Data Button
    col_upload_title, col_reset = st.columns([3, 1])
    with col_reset:
        if st.button("🔄 Reset to Synthetic Demo Data", use_container_width=True):
            fresh_data = load_default_data()
            for k, v in fresh_data.items():
                st.session_state["data_dict"][k] = v
            st.success("Successfully reset all datasets to default demo records!")
            st.rerun()

    # Uploaders for each of the 7 datasets
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "1. Suppliers", "2. Purchase Orders", "3. Inventory",
        "4. Production", "5. Transportation", "6. Demand", "7. BOM"
    ])

    tabs_map = {
        "suppliers": tab1,
        "purchase_orders": tab2,
        "inventory": tab3,
        "production": tab4,
        "transportation": tab5,
        "demand": tab6,
        "bill_of_materials": tab7
    }

    for name, tab in tabs_map.items():
        with tab:
            st.markdown(f"**Upload dataset:** `{name}.csv` or `{name}.xlsx`")
            up_file = st.file_uploader(
                f"Choose file for {name}",
                type=["csv", "xlsx", "xls"],
                key=f"uploader_{name}"
            )
            if up_file is not None:
                try:
                    loaded_df = load_file(up_file)
                    st.session_state["data_dict"][name] = loaded_df
                    st.success(f"Successfully loaded {len(loaded_df)} rows for '{name}'!")
                except Exception as e:
                    st.error(f"Error parsing file: {e}")

            # Display current dataset preview
            curr_df = data_dict.get(name)
            if curr_df is not None and not curr_df.empty:
                st.markdown(f"**Current active data preview ({len(curr_df)} rows, {len(curr_df.columns)} columns):**")
                st.dataframe(curr_df.head(6), use_container_width=True)
            else:
                st.warning(f"No active data for {name}.")

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 3. Validation Diagnostics & Schema Integrity
    st.markdown("### 🔍 Dataset Validation Diagnostics & Referential Integrity")

    val_tabs = st.tabs(["Schema Checks & Mapping", "Referential Integrity", "Analytical Feasibility"])

    with val_tabs[0]:
        st.markdown("#### Schema & Column Mapping Audit")
        val_summaries = []
        for name in DATASET_SCHEMAS.keys():
            df = data_dict.get(name)
            res = validate_dataset(df, name, DATASET_SCHEMAS[name])
            val_summaries.append({
                "Dataset": name,
                "Status": "Valid" if res["is_valid"] else "Missing / Invalid",
                "Row Count": res["row_count"],
                "Missing Columns": len(res["missing_columns"]),
                "Duplicate PKs": res["duplicates"],
                "Warnings": len(res["warnings"])
            })
        st.dataframe(pd.DataFrame(val_summaries), use_container_width=True)

    with val_tabs[1]:
        st.markdown("#### Cross-Table Referential Integrity")
        issues = check_referential_integrity(data_dict)
        if len(issues) == 0:
            render_alert("All foreign key relationships verified. No orphaned purchase orders, materials, or shipments detected.", alert_type="success", title="Referential Integrity Passed")
        else:
            for issue in issues:
                st.error(f"**{issue['relationship']}:** {issue['issue']}")

    with val_tabs[2]:
        st.markdown("#### Analytical Feasibility Audit")
        st.write("Downstream analytical capabilities evaluated based on current dataset presence:")
        feas = assess_analytical_feasibility(data_dict)
        feas_rows = []
        for mod_name, info in feas.items():
            feas_rows.append({
                "Analytical Module": mod_name,
                "Execution Feasibility": "Operational" if info["feasible"] else "Disabled / Partial",
                "Data Dependency & Notes": info["limitation"] or "All required data inputs present and validated."
            })
        st.dataframe(pd.DataFrame(feas_rows), use_container_width=True)

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
