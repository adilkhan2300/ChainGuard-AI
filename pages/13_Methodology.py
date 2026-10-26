"""
ChainGuard AI - Page 13: Methodology & AI Governance
Comprehensive mathematical formulation, risk index documentation,
machine learning leakage prevention protocols, and responsible AI governance.
"""

import streamlit as st
from utils.ui_components import apply_custom_styles, render_header, render_alert

def render_page(data_dict=None, filters=None):
    apply_custom_styles()
    render_header(
        title="Methodology, Mathematical Models & AI Governance",
        subtitle="Transparent documentation of algorithmic formulas, statistical indices, leakage safeguards, and governance principles"
    )

    m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs([
        "1. Inventory & Safety Stock Models",
        "2. Supplier Risk Index Formulation",
        "3. Machine Learning & Zero-Leakage Policy",
        "4. Financial Impact & Responsible AI"
    ])

    with m_tab1:
        st.markdown("### 📐 Inventory Optimization & Stockout Formulations")
        st.markdown("""
        #### 1. Net Available Stock
        $$\\text{Net Available Stock} = \\max(0, \\text{Current Physical Stock} - \\text{Reserved / Committed Stock})$$
        *Calculated strictly when current stock is non-negative.*

        #### 2. Days of Inventory Coverage
        $$\\text{Days of Coverage} = \\begin{cases} 
        \\frac{\\text{Net Available Stock}}{\\text{Average Daily Demand}}, & \\text{if } \\text{Average Daily Demand} > 0 \\\\
        \\infty, & \\text{if } \\text{Average Daily Demand} = 0
        \\end{cases}$$
        *Materials with coverage &lt; 7.0 days are classified as **Critical Stockout Risk**.*

        #### 3. Dynamic Statistical Safety Stock ($SS$)
        Under stochastic daily demand $\\sigma_D$ and stochastic supplier replenishment lead time $\\sigma_L$:
        $$SS = z \\times \\sqrt{L \\cdot \\sigma_D^2 + D^2 \\cdot \\sigma_L^2}$$
        Where:
        * $z$ is the inverse standard normal cumulative distribution function for target cycle service level (e.g., $z=1.65$ for 95%, $z=1.96$ for 97.5%, $z=2.33$ for 99%).
        * $L$ is the average supplier lead time (days).
        * $D$ is the average daily material consumption.
        * $\\sigma_D$ is the standard deviation of daily demand.
        * $\\sigma_L$ is the standard deviation of supplier lead time.

        #### 4. Optimal Dynamic Reorder Point ($ROP$)
        $$ROP = (D \\times L) + SS$$
        *A purchase order replenishment trigger is automatically generated whenever Net Available Stock falls below the calculated ROP.*
        """)

    with m_tab2:
        st.markdown("### 🏆 Supplier Risk Index Formulation")
        st.markdown("""
        The ChainGuard **Supplier Risk Score** is an empirical multi-factor index scaled from 0 (Best) to 100 (Worst), calculated as:

        $$\\text{Supplier Risk Score} = \\sum_{i=1}^{6} w_i \\times R_i$$

        | Factor ($R_i$) | Component Metric | Normalization Formula | Default Weight ($w_i$) |
        | :--- | :--- | :--- | :---: |
        | **1. Delivery Unreliability** | On-Time Delivery Rate ($OTD$) | $(1.0 - OTD) \\times 100$ | **25%** |
        | **2. Lead-Time Volatility** | Lead-Time Standard Deviation ($\\sigma_{LT}$) | $\\min(1.0, \\frac{\\sigma_{LT}}{10}) \\times 100$ | **20%** |
        | **3. Order Shortfall** | Historical Fulfillment Rate ($FR$) | $(1.0 - FR) \\times 100$ | **15%** |
        | **4. Quality Defect Score** | Recorded Quality Rating ($Q \\in [1, 5]$) | $\\frac{5.0 - Q}{4.0} \\times 100$ | **15%** |
        | **5. Financial Solvency Risk** | Financial Risk Indicator ($F \\in [0, 1]$) | $F \\times 100$ | **15%** |
        | **6. Single-Source Penalty** | Single-Source Component Count ($S$) | $\\min(100, S \\times 35)$ | **10%** |

        *Risk Tiers:* **Critical** (Score $\\ge 70$), **Elevated Risk** ($50 \\le \\text{Score} < 70$), **Moderate** ($30 \\le \\text{Score} < 50$), and **Low Risk** (Score $< 30$).
        """)

    with m_tab3:
        st.markdown("### 🤖 Disruption ML Engine & Strict Zero-Leakage Policy")
        st.markdown("""
        #### Prediction Target
        Binary classification where $Y = 1$ if a Purchase Order arrives late ($\text{Actual Delivery Date} > \text{Promised Date}$) or is delayed in open status; $Y = 0$ if delivered on or before promised delivery date.

        #### Strict Zero Target-Leakage Protocols
        To ensure authentic predictive capability before order release, the ML pipeline enforces rigorous feature separation:
        * **Allowed Features (Known at PO Placement):** Contractual lead time, historical vendor quality score, supplier financial risk score, ordered quantity, unit price, total order value, order placement month, and BOM criticality tier.
        * **Strictly Excluded Features (Forbidden Leakage):** Actual delivery date, actual arrival date, received quantity, observed delay days, and carrier delivery receipts.

        #### Model Implementations & Baselines
        1. **Naive Baseline:** `DummyClassifier(strategy='most_frequent')` representing the historical majority class.
        2. **Regularized Logistic Regression:** Scaled with `StandardScaler` and balanced class weighting.
        3. **Random Forest Classifier:** 100 decision trees, depth-constrained, providing Gini feature importances.
        4. **Gradient Boosting Classifier:** Sequential boosting minimizing log-loss.
        *Evaluated on Stratified Holdout Test Sets using Precision, Recall, F1, ROC-AUC, and PR-AUC.*
        """)

    with m_tab4:
        st.markdown("### 💰 Financial Exposure Allocation & Responsible AI Governance")
        st.markdown("""
        #### Financial Exposure Segregation
        To avoid double-counting across financial statements, cost drivers are classified into three distinct categories:
        1. **Actual Recorded Outlays:** Directly billed courier freight surcharges for expedited air shipments.
        2. **Calculated Working Capital Metrics:** Carrying cost on inventory units exceeding $2 \\times ROP$, evaluated at corporate holding rates ($22\%$ per annum).
        3. **Model-Based Statistical Estimates:** Manufacturing plant idle line capacity losses ($$1,200/day$) and customer SLA delivery penalty clauses ($2\%$ order value).

        #### Responsible AI & System Limitations
        * **No Data Invention:** The system never synthesizes fake supplier lead times or fictitious stock quantities when data is missing; it transparently marks analyses as unfeasible.
        * **No Telematics Monitoring:** Predictions are based on historical records and ERP timestamps. The system does not imply real-time satellite IoT tracking.
        * **Human-in-the-Loop:** All automated mitigation recommendations require managerial review and authorization before release to operational ERP systems.
        """)

if __name__ == "__main__":
    render_page()
