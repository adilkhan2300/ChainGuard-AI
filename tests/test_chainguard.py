"""
ChainGuard AI - Automated Test Suite
Validates data loading, schema validation, supplier risk computations,
inventory coverage, stockout projections, BOM explosion, ML disruption prediction,
leakage absence, scenario simulation, and PDF generation.
"""

import pytest
import os
import pandas as pd
import numpy as np

from modules.data_loader import load_default_data, DATASET_SCHEMAS
from modules.data_validation import validate_dataset, check_referential_integrity, standardize_columns
from modules.supplier_risk import calculate_supplier_metrics, calculate_composite_supplier_score
from modules.inventory_analysis import calculate_inventory_metrics, calculate_theoretical_safety_stock
from modules.production_risk import evaluate_production_material_risk
from modules.transportation_analysis import analyze_transportation_performance
from modules.disruption_prediction import prepare_po_prediction_data, train_and_evaluate_models
from modules.risk_scoring import generate_integrated_risk_alerts
from modules.mitigation_engine import generate_rule_based_mitigations
from modules.strategy_cost_comparison import evaluate_mitigation_strategies
from modules.scenario_simulator import simulate_supply_chain_scenario
from modules.financial_analysis import compute_financial_impact_breakdown
from modules.reporting import generate_pdf_report, generate_multi_tab_excel

@pytest.fixture
def default_data():
    """Loads all default datasets generated in data/ folder."""
    return load_default_data()

def test_data_loader_schemas(default_data):
    """Verifies that all 7 datasets are loaded and match expected schema keys."""
    assert len(default_data) == 7
    for key, cols in DATASET_SCHEMAS.items():
        df = default_data[key]
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, f"Dataset {key} should have rows"
        for col in cols:
            assert col in df.columns, f"Missing {col} in {key}"

def test_data_validation(default_data):
    """Checks schema validation and referential integrity."""
    val_res = validate_dataset(default_data["suppliers"], "suppliers", DATASET_SCHEMAS["suppliers"])
    assert val_res["is_valid"] is True
    assert val_res["duplicates"] == 0

    integrity_issues = check_referential_integrity(default_data)
    assert isinstance(integrity_issues, list)
    # Synthetic data should be referentially consistent
    assert len(integrity_issues) == 0

def test_supplier_risk_calculations(default_data):
    """Tests supplier OTD rate, lead-time variance, and composite score."""
    sups_df = default_data["suppliers"]
    pos_df = default_data["purchase_orders"]
    bom_df = default_data["bill_of_materials"]

    metrics = calculate_supplier_metrics(sups_df, pos_df, bom_df)
    assert len(metrics) == len(sups_df)
    assert "on_time_delivery_rate" in metrics.columns
    assert "supplier_risk_score" in metrics.columns
    assert "risk_level" in metrics.columns

    # Verify score bounds
    assert (metrics["supplier_risk_score"] >= 0).all()
    assert (metrics["supplier_risk_score"] <= 100).all()

def test_inventory_coverage_and_stockouts(default_data):
    """Validates Net Available Stock, Days of Coverage, and stockout risk logic."""
    inv_df = default_data["inventory"]
    pos_df = default_data["purchase_orders"]

    enriched_inv = calculate_inventory_metrics(inv_df, pos_df)
    assert len(enriched_inv) == len(inv_df)
    assert "net_available_stock" in enriched_inv.columns
    assert "days_of_coverage" in enriched_inv.columns
    assert "inventory_status" in enriched_inv.columns

    # Net stock must be non-negative
    assert (enriched_inv["net_available_stock"] >= 0).all()

    # Safety stock theoretical formula
    ss = calculate_theoretical_safety_stock(avg_demand=20.0, demand_std=4.0, lead_time_days=25, lt_std=3.0, service_level=0.95)
    assert ss > 0
    assert isinstance(ss, int)

def test_production_bom_risk(default_data):
    """Validates BOM explosion, material requirements, shortage detection, and impact cost."""
    prod_df = default_data["production"]
    bom_df = default_data["bill_of_materials"]
    inv_df = default_data["inventory"]
    po_df = default_data["purchase_orders"]

    eval_df, summary = evaluate_production_material_risk(prod_df, bom_df, inv_df, po_df)
    assert len(eval_df) == len(prod_df)
    assert "potential_delay_days" in eval_df.columns
    assert "estimated_production_impact_cost" in eval_df.columns
    assert summary["total_production_orders"] == len(prod_df)
    assert summary["total_impact_cost"] >= 0.0

def test_transportation_analysis(default_data):
    """Validates carrier metrics and transit delay analysis."""
    trans_df = default_data["transportation"]
    df_car, df_route, summary = analyze_transportation_performance(trans_df)
    assert len(df_car) > 0
    assert "reliability_score" in df_car.columns
    assert summary["total_shipments"] == len(trans_df)

def test_disruption_ml_pipeline_and_no_leakage(default_data):
    """Validates ML dataset preparation, leakage prevention, and model performance."""
    pos_df = default_data["purchase_orders"]
    sups_df = default_data["suppliers"]
    bom_df = default_data["bill_of_materials"]

    clean_df, feature_cols = prepare_po_prediction_data(pos_df, sups_df, bom_df)
    assert clean_df is not None
    assert len(clean_df) > 20
    assert "target_is_delayed" in clean_df.columns

    # STRICT LEAKAGE CHECK: actual delivery date and received qty must NOT be in feature_cols
    forbidden_leakage = ["actual_delivery_date", "actual_dt", "quantity_received", "delay_days", "actual_lead_time"]
    for f in forbidden_leakage:
        assert f not in feature_cols

    res = train_and_evaluate_models(clean_df, feature_cols)
    assert res is not None
    assert "Random Forest" in res["results"]
    assert "Logistic Regression" in res["results"]
    rf_metrics = res["results"]["Random Forest"]
    assert "roc_auc" in rf_metrics
    assert "confusion_matrix" in rf_metrics
    assert rf_metrics["roc_auc"] >= 0.5

def test_scenario_simulator(default_data):
    """Tests what-if simulations with lead time and demand shocks."""
    inv_df = calculate_inventory_metrics(default_data["inventory"], default_data["purchase_orders"])
    prod_eval, _ = evaluate_production_material_risk(
        default_data["production"], default_data["bill_of_materials"], default_data["inventory"]
    )
    sup_metrics = calculate_supplier_metrics(default_data["suppliers"], default_data["purchase_orders"])

    comparison, sim_inv, sim_prod = simulate_supply_chain_scenario(
        base_inv_df=inv_df,
        base_prod_df=prod_eval,
        base_sup_df=sup_metrics,
        lead_time_shock_days=10,
        demand_surge_pct=25.0
    )
    assert "baseline" in comparison
    assert "scenario" in comparison
    assert "deltas" in comparison
    # Shocks should increase risk or maintain
    assert len(sim_inv) == len(inv_df)

def test_financial_and_mitigation_engines(default_data):
    """Tests financial breakdown and mitigation playbooks."""
    inv_df = calculate_inventory_metrics(default_data["inventory"], default_data["purchase_orders"])
    prod_eval, _ = evaluate_production_material_risk(
        default_data["production"], default_data["bill_of_materials"], default_data["inventory"]
    )
    df_cost, fin_sum = compute_financial_impact_breakdown(
        inv_df, prod_eval, default_data["purchase_orders"], default_data["transportation"]
    )
    assert fin_sum["total_financial_exposure"] > 0
    assert len(df_cost) >= 4

    # Test Strategy Cost Comparison
    strat_df = evaluate_mitigation_strategies("MAT-101", 300, target_date_days=7)
    assert len(strat_df) == 5
    assert strat_df["is_recommended"].sum() == 1

def test_reporting_pdf_generation(default_data):
    """Tests ReportLab PDF compilation to valid bytes without crashing."""
    inv_df = calculate_inventory_metrics(default_data["inventory"], default_data["purchase_orders"])
    prod_eval, _ = evaluate_production_material_risk(
        default_data["production"], default_data["bill_of_materials"], default_data["inventory"]
    )
    sup_metrics = calculate_supplier_metrics(default_data["suppliers"], default_data["purchase_orders"])
    alerts = generate_integrated_risk_alerts(inv_df, sup_metrics, prod_eval, default_data["transportation"])
    _, fin_sum = compute_financial_impact_breakdown(inv_df, prod_eval, default_data["purchase_orders"], default_data["transportation"])

    pdf_bytes = generate_pdf_report(alerts, sup_metrics, inv_df, prod_eval, fin_sum)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
