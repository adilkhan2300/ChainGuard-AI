"""
ChainGuard AI - Data Loader Module
Handles loading of synthetic default data or uploaded user CSV/Excel files.
Provides caching and downloadable templates.
"""

import os
import io
import pandas as pd
import streamlit as st

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

EXPECTED_DATASETS = [
    "suppliers",
    "purchase_orders",
    "inventory",
    "production",
    "transportation",
    "demand",
    "bill_of_materials"
]

DATASET_SCHEMAS = {
    "suppliers": [
        "supplier_id", "supplier_name", "supplier_location", "material_categories",
        "contractual_lead_time_days", "supplier_capacity", "quality_rating",
        "financial_risk_score", "supplier_status"
    ],
    "purchase_orders": [
        "purchase_order_id", "supplier_id", "material_id", "order_date",
        "promised_delivery_date", "actual_delivery_date", "quantity_ordered",
        "quantity_received", "unit_cost", "purchase_order_status"
    ],
    "inventory": [
        "material_id", "material_name", "plant_id", "current_stock",
        "reserved_stock", "safety_stock", "reorder_point", "average_daily_demand",
        "inventory_unit_cost", "inventory_date"
    ],
    "production": [
        "production_order_id", "product_id", "plant_id", "planned_start_date",
        "planned_completion_date", "actual_completion_date", "planned_quantity",
        "completed_quantity", "production_status", "material_id", "material_quantity_required"
    ],
    "transportation": [
        "shipment_id", "purchase_order_id", "carrier_id", "transport_mode",
        "origin", "destination", "shipment_date", "estimated_arrival_date",
        "actual_arrival_date", "shipment_status", "shipping_cost"
    ],
    "demand": [
        "product_id", "material_id", "forecast_date", "forecast_quantity",
        "actual_demand", "demand_variability"
    ],
    "bill_of_materials": [
        "product_id", "material_id", "quantity_required_per_unit",
        "material_criticality", "approved_alternative_material"
    ]
}

def load_default_data():
    """Loads all default datasets from the data/ folder."""
    data_dict = {}
    for name in EXPECTED_DATASETS:
        file_path = os.path.join(DEFAULT_DATA_DIR, f"{name}.csv")
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                data_dict[name] = df
            except Exception as e:
                st.error(f"Error loading default dataset {name}: {e}")
                data_dict[name] = pd.DataFrame(columns=DATASET_SCHEMAS.get(name, []))
        else:
            data_dict[name] = pd.DataFrame(columns=DATASET_SCHEMAS.get(name, []))
    return data_dict

def load_file(uploaded_file):
    """Loads an uploaded CSV or Excel file into a pandas DataFrame."""
    try:
        filename = uploaded_file.name.lower()
        if filename.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif filename.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
    except Exception as e:
        raise ValueError(f"Failed to parse uploaded file: {str(e)}")

def generate_csv_template(dataset_name):
    """Generates a downloadable CSV template with headers and sample row."""
    columns = DATASET_SCHEMAS.get(dataset_name, [])
    # Sample row templates
    samples = {
        "suppliers": ["SUP-001", "Example Tech Ltd", "Taipei, Taiwan", "Electronics", 30, 100000, 4.5, 0.12, "Active"],
        "purchase_orders": ["PO-1001", "SUP-001", "MAT-101", "2026-01-15", "2026-02-15", "2026-02-14", 500, 500, 45.0, "Delivered On-Time"],
        "inventory": ["MAT-101", "ARM Microcontroller", "PL-NORTH", 850, 150, 200, 500, 15.5, 45.0, "2026-09-15"],
        "production": ["PRD-8001", "PROD-01", "PL-NORTH", "2026-09-01", "2026-09-15", "", 100, 0, "Scheduled Confirmed", "MAT-101", 100],
        "transportation": ["SHP-5001", "PO-1001", "CAR-01", "Air", "Taipei, Taiwan", "PL-NORTH", "2026-01-20", "2026-01-25", "2026-01-25", "Delivered On-Time", 1250.0],
        "demand": ["PROD-01", "MAT-101", "2026-01-05", 200, 215, 0.075],
        "bill_of_materials": ["PROD-01", "MAT-101", 1.0, "Critical", "MAT-102"]
    }
    sample_row = samples.get(dataset_name, [""] * len(columns))
    df = pd.DataFrame([sample_row], columns=columns)
    return df.to_csv(index=False).encode("utf-8")

def generate_all_templates_excel():
    """Generates an Excel workbook containing blank/sample sheets for all 7 datasets."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, cols in DATASET_SCHEMAS.items():
            sample_df = pd.DataFrame(columns=cols)
            sample_df.to_excel(writer, sheet_name=name[:31], index=False)
    return output.getvalue()
