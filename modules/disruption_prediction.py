"""
ChainGuard AI - Machine Learning Disruption Prediction Engine
Trains supervised classification models (Logistic Regression, Random Forest, Gradient Boosting)
to predict Purchase Order delivery delays without target leakage.
Provides evaluation metrics (Precision, Recall, F1, ROC-AUC, PR-AUC), confusion matrices,
feature importances, baseline comparisons, and real-time interactive inference.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, roc_curve, precision_recall_curve
)

def prepare_po_prediction_data(po_df, suppliers_df, bom_df=None):
    """
    Builds a clean, leakage-free dataset for predicting PO delivery delays.
    Features used are ONLY those known at order booking time:
      - Supplier contractual lead time
      - Supplier financial risk score
      - Supplier quality rating
      - Order quantity
      - Unit cost
      - Total order value
      - Order month
      - Material criticality (from BOM if available)
    Target:
      - 1 if delivered late (delay > 0) or delayed open, 0 if delivered on-time.
    """
    if po_df is None or po_df.empty or suppliers_df is None or suppliers_df.empty:
        return pd.DataFrame(), None

    pos = po_df.copy()
    sups = suppliers_df.copy()

    # Dates parsing
    pos["order_dt"] = pd.to_datetime(pos["order_date"], errors="coerce")
    pos["promised_dt"] = pd.to_datetime(pos["promised_delivery_date"], errors="coerce")
    pos["actual_dt"] = pd.to_datetime(pos["actual_delivery_date"], errors="coerce")

    # Define Target: 1 = Delayed, 0 = On-Time
    # Filter only completed orders or delayed orders for reliable training
    # Orders that are completed have actual_dt
    completed_mask = pos["actual_dt"].notna()
    delayed_open_mask = pos["purchase_order_status"].astype(str).str.contains("Delayed", case=False, na=False)
    
    labeled_pos = pos[completed_mask | delayed_open_mask].copy()
    if len(labeled_pos) < 20:
        return pd.DataFrame(), None

    # Calculate target label on labeled_pos
    delay_days = (labeled_pos["actual_dt"] - labeled_pos["promised_dt"]).dt.days
    is_delayed_open = labeled_pos["purchase_order_status"].astype(str).str.contains("Delayed", case=False, na=False)
    labeled_pos["target_is_delayed"] = np.where(
        (delay_days > 0) | is_delayed_open,
        1,
        0
    )

    # Merge supplier attributes
    sup_features = sups[[
        "supplier_id", "contractual_lead_time_days",
        "quality_rating", "financial_risk_score"
    ]].copy()
    
    merged = pd.merge(labeled_pos, sup_features, on="supplier_id", how="left")

    # Merge BOM criticality
    if bom_df is not None and not bom_df.empty:
        crit_map = bom_df.drop_duplicates(subset=["material_id"])[["material_id", "material_criticality"]]
        merged = pd.merge(merged, crit_map, on="material_id", how="left")
        merged["material_criticality"] = merged["material_criticality"].fillna("Medium")
    else:
        merged["material_criticality"] = "Medium"

    # Leakage-Free Feature Engineering
    merged["order_month"] = merged["order_dt"].dt.month.fillna(1).astype(int)
    merged["total_order_value"] = merged["quantity_ordered"] * merged["unit_cost"]
    merged["contractual_lead_time_days"] = pd.to_numeric(merged["contractual_lead_time_days"], errors="coerce").fillna(30.0)
    merged["quality_rating"] = pd.to_numeric(merged["quality_rating"], errors="coerce").fillna(4.0)
    merged["financial_risk_score"] = pd.to_numeric(merged["financial_risk_score"], errors="coerce").fillna(0.2)
    merged["quantity_ordered"] = pd.to_numeric(merged["quantity_ordered"], errors="coerce").fillna(100.0)
    merged["unit_cost"] = pd.to_numeric(merged["unit_cost"], errors="coerce").fillna(10.0)

    feature_cols = [
        "contractual_lead_time_days",
        "quality_rating",
        "financial_risk_score",
        "quantity_ordered",
        "unit_cost",
        "total_order_value",
        "order_month",
        "material_criticality"
    ]

    clean_df = merged[feature_cols + ["target_is_delayed"]].dropna().copy()
    return clean_df, feature_cols

def train_and_evaluate_models(clean_df, feature_cols, test_size=0.25, random_state=42):
    """
    Trains Logistic Regression, Random Forest, and Gradient Boosting models.
    Compares against a Dummy Classifier baseline and outputs all performance metrics.
    """
    if clean_df is None or len(clean_df) < 20:
        return None

    X = clean_df[feature_cols]
    y = clean_df["target_is_delayed"].astype(int)

    # Check class balance
    if y.nunique() < 2:
        return None

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    numeric_features = [
        "contractual_lead_time_days", "quality_rating", "financial_risk_score",
        "quantity_ordered", "unit_cost", "total_order_value", "order_month"
    ]
    categorical_features = ["material_criticality"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    models = {
        "Baseline (Majority Class)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(class_weight="balanced", random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", random_state=random_state),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=80, max_depth=3, random_state=random_state)
    }

    results = {}
    fitted_pipelines = {}

    for name, clf in models.items():
        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        pipe.fit(X_train, y_train)
        fitted_pipelines[name] = pipe

        preds = pipe.predict(X_test)
        
        # Probabilities
        if hasattr(pipe.named_steps["classifier"], "predict_proba"):
            probs = pipe.predict_proba(X_test)[:, 1]
            try:
                auc_roc = round(roc_auc_score(y_test, probs), 3)
                pr_auc = round(average_precision_score(y_test, probs), 3)
            except Exception:
                auc_roc = 0.5
                pr_auc = 0.5
        else:
            probs = preds
            auc_roc = 0.5
            pr_auc = 0.5

        # Confusion Matrix
        cm = confusion_matrix(y_test, preds)

        results[name] = {
            "accuracy": round((preds == y_test).mean(), 3),
            "precision": round(precision_score(y_test, preds, zero_division=0), 3),
            "recall": round(recall_score(y_test, preds, zero_division=0), 3),
            "f1": round(f1_score(y_test, preds, zero_division=0), 3),
            "roc_auc": auc_roc,
            "pr_auc": pr_auc,
            "confusion_matrix": cm,
            "y_test": y_test.values,
            "y_probs": probs
        }

    # Extract feature importance from Random Forest
    rf_pipe = fitted_pipelines["Random Forest"]
    rf_model = rf_pipe.named_steps["classifier"]
    onehot_cols = rf_pipe.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_features)
    all_feature_names = numeric_features + list(onehot_cols)
    importances = rf_model.feature_importances_

    df_imp = pd.DataFrame({
        "Feature": all_feature_names,
        "Importance": importances
    }).sort_values("Importance", ascending=False)

    return {
        "results": results,
        "fitted_pipelines": fitted_pipelines,
        "feature_importance": df_imp,
        "feature_cols": feature_cols,
        "test_sample_count": len(y_test),
        "class_balance_delay_pct": round((y.sum() / len(y)) * 100, 1)
    }

def predict_new_order_delay_probability(fitted_pipeline, order_dict):
    """
    Interactive inference: predicts the probability of delay for a single purchase order.
    """
    df_single = pd.DataFrame([order_dict])
    prob_delay = fitted_pipeline.predict_proba(df_single)[0, 1]
    return round(float(prob_delay), 3)
