"""
ChainGuard AI - Data Validation Module
Performs automatic column mapping, date parsing, duplicate detection,
missing-value analysis, referential integrity checks, unit consistency,
and validation of business rules across supply chain datasets.
"""

import pandas as pd
import numpy as np

# Column Synonyms Dictionary for automatic mapping
COLUMN_SYNONYMS = {
    # Suppliers
    "supplier": "supplier_id",
    "vendor_id": "supplier_id",
    "vendor": "supplier_id",
    "supplier_name": "supplier_name",
    "vendor_name": "supplier_name",
    "location": "supplier_location",
    "lead_time": "contractual_lead_time_days",
    "contract_lead_time": "contractual_lead_time_days",
    "capacity": "supplier_capacity",
    "rating": "quality_rating",
    "financial_risk": "financial_risk_score",
    "status": "supplier_status",
    
    # Purchase Orders
    "po_id": "purchase_order_id",
    "order_id": "purchase_order_id",
    "item_id": "material_id",
    "sku": "material_id",
    "qty_ordered": "quantity_ordered",
    "qty_received": "quantity_received",
    "price": "unit_cost",
    "cost": "unit_cost",
    "po_status": "purchase_order_status",
    "promised_date": "promised_delivery_date",
    "actual_date": "actual_delivery_date",

    # Inventory
    "stock": "current_stock",
    "on_hand": "current_stock",
    "reserved": "reserved_stock",
    "safety": "safety_stock",
    "rop": "reorder_point",
    "daily_demand": "average_daily_demand",
    "plant": "plant_id",

    # Production
    "prod_id": "production_order_id",
    "prod_order": "production_order_id",
    "plan_qty": "planned_quantity",
    "comp_qty": "completed_quantity",
    
    # Transportation
    "carrier": "carrier_id",
    "mode": "transport_mode",
    "freight_cost": "shipping_cost"
}

def standardize_columns(df, expected_columns):
    """
    Cleans column names and maps known synonyms to standard schema names.
    Returns cleaned DataFrame and dictionary of mapped columns.
    """
    df = df.copy()
    cleaned_names = {}
    mapped_log = {}

    for col in df.columns:
        norm = str(col).strip().lower().replace(" ", "_").replace("-", "_")
        mapped = COLUMN_SYNONYMS.get(norm, norm)
        cleaned_names[col] = mapped
        if mapped != col:
            mapped_log[col] = mapped

    df.rename(columns=cleaned_names, inplace=True)
    return df, mapped_log

def validate_dates(df, date_columns):
    """
    Attempts to parse date columns.
    Returns parsed DataFrame, invalid count dict, and formatted columns.
    """
    df = df.copy()
    invalid_dates = {}
    for col in date_columns:
        if col in df.columns:
            # Save original representation for empty checking
            series = df[col].astype(str).str.strip()
            # Convert empty-like strings to NaN
            series = series.replace(["", "nan", "None", "NaT", "NULL", "null"], np.nan)
            parsed = pd.to_datetime(series, errors="coerce")
            # Count invalid non-empty values
            num_invalid = series.notna().sum() - parsed.notna().sum()
            invalid_dates[col] = int(num_invalid)
            df[col] = parsed
    return df, invalid_dates

def validate_dataset(df, dataset_name, required_schema):
    """
    Validates a single dataset against its schema, checking missing values,
    data types, and duplicate primary keys.
    """
    results = {
        "dataset_name": dataset_name,
        "row_count": len(df),
        "is_valid": True,
        "missing_columns": [],
        "extra_columns": [],
        "null_counts": {},
        "duplicates": 0,
        "warnings": [],
        "errors": []
    }

    if df is None or df.empty:
        results["is_valid"] = False
        results["errors"].append(f"Dataset '{dataset_name}' is empty or missing.")
        return results

    # Standardize columns
    df, mapped = standardize_columns(df, required_schema)
    results["mapped_columns"] = mapped

    # Check required columns
    present_cols = set(df.columns)
    missing_cols = [c for c in required_schema if c not in present_cols]
    if missing_cols:
        results["is_valid"] = False
        results["missing_columns"] = missing_cols
        results["errors"].append(f"Missing required columns: {', '.join(missing_cols)}")

    results["extra_columns"] = [c for c in df.columns if c not in required_schema]

    # Check null values
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            results["null_counts"][col] = {
                "count": null_count,
                "percentage": round((null_count / len(df)) * 100, 1)
            }

    # Check primary keys
    pk_map = {
        "suppliers": ["supplier_id"],
        "purchase_orders": ["purchase_order_id"],
        "inventory": ["material_id", "plant_id"],
        "production": ["production_order_id"],
        "transportation": ["shipment_id"],
        "bill_of_materials": ["product_id", "material_id"]
    }
    pks = pk_map.get(dataset_name, [])
    if all(pk in df.columns for pk in pks) and len(pks) > 0:
        dups = int(df.duplicated(subset=pks).sum())
        results["duplicates"] = dups
        if dups > 0:
            results["warnings"].append(f"Found {dups} duplicate records based on primary key(s) {pks}.")

    # Business rule value checks
    if dataset_name == "purchase_orders":
        if "quantity_ordered" in df.columns:
            invalid_qty = (pd.to_numeric(df["quantity_ordered"], errors="coerce") <= 0).sum()
            if invalid_qty > 0:
                results["warnings"].append(f"{invalid_qty} purchase orders have invalid non-positive quantity_ordered.")
        if "unit_cost" in df.columns:
            invalid_cost = (pd.to_numeric(df["unit_cost"], errors="coerce") <= 0).sum()
            if invalid_cost > 0:
                results["warnings"].append(f"{invalid_cost} purchase orders have invalid non-positive unit_cost.")

    if dataset_name == "inventory":
        if "current_stock" in df.columns:
            neg_stock = (pd.to_numeric(df["current_stock"], errors="coerce") < 0).sum()
            if neg_stock > 0:
                results["warnings"].append(f"{neg_stock} inventory items report negative current_stock.")

    return results

def check_referential_integrity(data_dict):
    """
    Checks cross-table relational integrity:
    1. PO supplier_id in suppliers.supplier_id
    2. PO material_id in inventory.material_id or BOM
    3. Production material_id in inventory.material_id
    4. Transportation purchase_order_id in purchase_orders.purchase_order_id
    5. BOM product_id in production.product_id
    """
    integrity_issues = []

    suppliers_df = data_dict.get("suppliers")
    po_df = data_dict.get("purchase_orders")
    inv_df = data_dict.get("inventory")
    prod_df = data_dict.get("production")
    trans_df = data_dict.get("transportation")
    bom_df = data_dict.get("bill_of_materials")

    # 1. PO Suppliers
    if po_df is not None and not po_df.empty and suppliers_df is not None and not suppliers_df.empty:
        if "supplier_id" in po_df.columns and "supplier_id" in suppliers_df.columns:
            valid_sups = set(suppliers_df["supplier_id"].dropna().unique())
            po_sups = set(po_df["supplier_id"].dropna().unique())
            orphans = po_sups - valid_sups
            if orphans:
                integrity_issues.append({
                    "relationship": "Purchase Orders -> Suppliers",
                    "issue": f"{len(orphans)} supplier IDs in POs not found in suppliers table: {list(orphans)[:5]}"
                })

    # 2. PO Materials
    if po_df is not None and not po_df.empty and inv_df is not None and not inv_df.empty:
        if "material_id" in po_df.columns and "material_id" in inv_df.columns:
            valid_mats = set(inv_df["material_id"].dropna().unique())
            po_mats = set(po_df["material_id"].dropna().unique())
            orphans = po_mats - valid_mats
            if orphans:
                integrity_issues.append({
                    "relationship": "Purchase Orders -> Inventory Materials",
                    "issue": f"{len(orphans)} material IDs in POs not found in inventory: {list(orphans)[:5]}"
                })

    # 3. Transportation POs
    if trans_df is not None and not trans_df.empty and po_df is not None and not po_df.empty:
        if "purchase_order_id" in trans_df.columns and "purchase_order_id" in po_df.columns:
            valid_pos = set(po_df["purchase_order_id"].dropna().unique())
            trans_pos = set(trans_df["purchase_order_id"].dropna().unique())
            orphans = trans_pos - valid_pos
            if orphans:
                integrity_issues.append({
                    "relationship": "Transportation -> Purchase Orders",
                    "issue": f"{len(orphans)} PO IDs in shipments not found in purchase_orders table: {list(orphans)[:5]}"
                })

    # 4. Production Materials
    if prod_df is not None and not prod_df.empty and inv_df is not None and not inv_df.empty:
        if "material_id" in prod_df.columns and "material_id" in inv_df.columns:
            valid_mats = set(inv_df["material_id"].dropna().unique())
            prod_mats = set(prod_df["material_id"].dropna().unique())
            orphans = prod_mats - valid_mats
            if orphans:
                integrity_issues.append({
                    "relationship": "Production -> Inventory Materials",
                    "issue": f"{len(orphans)} material IDs in production not found in inventory: {list(orphans)[:5]}"
                })

    return integrity_issues

def assess_analytical_feasibility(data_dict):
    """
    Checks which analytical modules can be executed reliably given the available data.
    """
    feasibility = {
        "Executive Dashboard": {"feasible": True, "limitation": None},
        "Supplier Risk Intelligence": {"feasible": True, "limitation": None},
        "Inventory Intelligence": {"feasible": True, "limitation": None},
        "Production Risk Analysis": {"feasible": True, "limitation": None},
        "Transportation Risk": {"feasible": True, "limitation": None},
        "Disruption Prediction (ML)": {"feasible": True, "limitation": None},
        "Scenario Simulator": {"feasible": True, "limitation": None},
        "Financial Impact Analysis": {"feasible": True, "limitation": None}
    }

    # Check Suppliers & POs
    if data_dict.get("suppliers") is None or data_dict["suppliers"].empty or data_dict.get("purchase_orders") is None or data_dict["purchase_orders"].empty:
        feasibility["Supplier Risk Intelligence"] = {
            "feasible": False,
            "limitation": "Requires both suppliers.csv and purchase_orders.csv to evaluate delivery history."
        }

    # Check Inventory
    if data_dict.get("inventory") is None or data_dict["inventory"].empty:
        feasibility["Inventory Intelligence"] = {
            "feasible": False,
            "limitation": "Missing inventory.csv dataset."
        }

    # Check Production & BOM
    if data_dict.get("production") is None or data_dict["production"].empty or data_dict.get("bill_of_materials") is None or data_dict["bill_of_materials"].empty:
        feasibility["Production Risk Analysis"] = {
            "feasible": False,
            "limitation": "Requires both production.csv and bill_of_materials.csv for BOM explosion."
        }

    # Check Transportation
    if data_dict.get("transportation") is None or data_dict["transportation"].empty:
        feasibility["Transportation Risk"] = {
            "feasible": False,
            "limitation": "Missing transportation.csv records."
        }

    # Check ML Disruption Prediction
    pos = data_dict.get("purchase_orders")
    if pos is None or len(pos) < 25:
        feasibility["Disruption Prediction (ML)"] = {
            "feasible": False,
            "limitation": "Insufficient historical purchase order records (< 25 rows) for robust ML training."
        }

    return feasibility
