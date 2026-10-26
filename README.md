# ChainGuard AI — Supply Chain Risk Prediction & Resilience Intelligence Platform

An enterprise AI-powered operations intelligence system designed to detect emerging supply chain risks early, predict disruptions before they halt manufacturing lines, estimate disruption financial exposure, and generate proactive mitigation playbooks.

Built for **MBA General Management, Operations Management, and Data Science & AI projects**.

---

## 🌟 Key Capabilities

1. **Executive Supply Chain Dashboard (14 Core KPIs):**
   - Active suppliers, managed SKUs, open purchase orders, total inventory value, items below ROP, critical stockouts, elevated-risk suppliers, delayed POs, average lead times, OTD rates, transit delays, production orders at risk, customer deliveries at risk, and total estimated disruption financial exposure.
2. **Data Integration & Validation Hub:**
   - Multi-file CSV and Excel upload management with automatic column normalization and synonym mapping.
   - Referential integrity verification across suppliers, POs, inventory, BOM, production, and transportation.
   - Downloadable formatted data templates (CSV & Master Excel workbook).
3. **Supplier Risk Intelligence:**
   - Evaluates delivery delays, lead-time standard deviation, historical on-time delivery (OTD) rates, fulfillment shortfalls, quality ratings, financial risk scores, geographic sourcing concentration, and single-source dependencies.
   - Configurable multi-factor risk weighting formula with interactive supplier drill-down.
4. **Inventory Intelligence & Stockout Prediction:**
   - Computes Net Available Stock ($Current - Reserved$) and Days of Coverage ($\frac{Net Available Stock}{Demand}$).
   - Predicts projected stockout dates and tracks incoming replenishment POs.
   - Interactive statistical safety stock calculator based on demand and lead-time variability:
     $$SS = z \times \sqrt{L \cdot \sigma_D^2 + D^2 \cdot \sigma_L^2}$$
5. **Production Disruption Analysis:**
   - Multi-level BOM explosion mapping production orders to component availability.
   - Quantifies material shortages, manufacturing delay windows, and plant idle-line impact costs ($1,200/day).
6. **Transportation & Delivery Risk:**
   - Carrier SLA reliability scorecards, corridor-level transit delay tracking, and freight spend analysis across Air, Ocean, Road, and Rail.
7. **Machine Learning Disruption Prediction Engine:**
   - Supervised classification models: **Logistic Regression, Random Forest, and Gradient Boosting**.
   - **Zero Target-Leakage Guarantee:** Trained strictly on attributes available at order placement date.
   - Precision, Recall, F1, ROC-AUC, PR-AUC, confusion matrices, and comparison against a naive baseline.
   - Interactive Real-Time Prediction Sandbox for pending purchase orders.
8. **AI-Powered Risk Alerts & Mitigation Playbooks:**
   - Standardized 8-point operational risk alerts (evidence, timing, financial exposure, team assignment, KPI).
   - Domain-specific action playbooks across Supplier, Inventory, Production, and Logistics.
   - Optional OpenAI API integration with a 100% functional deterministic MBA-grade rule-based fallback.
9. **Strategy Cost & Trade-off Comparison:**
   - Evaluates 5 response strategies for component shortages: Air Freight Expediting, Alternative Supplier, Inter-Plant Stock Transfer, Approved Substitute, and Order Rescheduling.
   - Multi-criteria decision matrix with cost, lead time, recovered volume, residual gap, and feasibility.
10. **Interactive Scenario Simulator:**
    - Dynamic What-If sensitivity modeling with sliders for lead time shifts, demand surges, safety stock multipliers, and emergency expediting interventions.
    - Side-by-side Baseline vs Scenario comparison with delta metrics.
11. **Financial Disruption Impact Analysis:**
    - Audited breakdown distinguishing actual recorded expenses, calculated metrics, and model-based estimates (idle line losses, customer SLA penalties, excess inventory holding costs).
12. **Executive Reports & Data Exports:**
    - One-click board-ready PDF audit report generation using ReportLab.
    - Master multi-tab Excel workbook export (.xlsx) and granular CSV extracts.
13. **Methodology & Responsible AI Governance:**
    - Complete mathematical formulation, ethical AI boundaries, and data limitations documentation.

---

## 🛠️ Technology Stack

- **Frontend & App Framework:** Streamlit
- **Data Engineering:** Pandas, NumPy
- **Visualizations:** Plotly Interactive Graphs & Dashboards
- **Machine Learning:** Scikit-learn (Logistic Regression, Random Forest, Gradient Boosting, Pipelines)
- **Time-Series & Forecasting:** Statsmodels, Scikit-learn
- **PDF Report Generation:** ReportLab
- **Excel & CSV Processing:** Openpyxl, Python CSV engine
- **LLM Integration:** OpenAI API (with built-in deterministic rule-based fallback)
- **Testing:** Pytest

---

## 📂 Project Architecture

```
PB8/
├── app.py                          # Master Streamlit application & navigation router
├── requirements.txt                # Python dependencies
├── README.md                       # Comprehensive system documentation
├── .env.example                    # Environment configuration template
├── modules/
│   ├── __init__.py
│   ├── data_loader.py              # File loading, caching & template generator
│   ├── data_validation.py          # Schema mapping, validation & referential integrity
│   ├── supplier_risk.py            # Lead-time variance, OTD, single-source & risk scoring
│   ├── inventory_analysis.py       # Net stock, coverage days, ROP & statistical safety stock
│   ├── demand_forecasting.py       # Statistical smoothing, accuracy & spike detection
│   ├── production_risk.py          # BOM explosion, shortage quantification & delay windows
│   ├── transportation_analysis.py  # Carrier SLAs, route delay patterns & freight spend
│   ├── disruption_prediction.py    # Leakage-free ML classification models & inference
│   ├── risk_scoring.py             # Multi-factor composite index & 8-point alerts
│   ├── mitigation_engine.py        # Operational mitigation playbooks across 4 domains
│   ├── strategy_cost_comparison.py # Decision support matrix for shortage options
│   ├── scenario_simulator.py       # Interactive what-if stress simulation engine
│   ├── financial_analysis.py       # Segregated financial exposure quantification
│   ├── llm_recommendations.py      # LLM synthesis & deterministic rule-based engine
│   └── reporting.py                # ReportLab PDF generator & multi-tab Excel exporter
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_Data_Upload_and_Validation.py
│   ├── 3_Supplier_Risk_Intelligence.py
│   ├── 4_Inventory_Intelligence.py
│   ├── 5_Production_Risk_Analysis.py
│   ├── 6_Transportation_Risk.py
│   ├── 7_Disruption_Prediction.py
│   ├── 8_Risk_Alerts_and_Mitigation.py
│   ├── 9_Strategy_Cost_Comparison.py
│   ├── 10_Scenario_Simulator.py
│   ├── 11_Financial_Impact.py
│   ├── 12_Reports_and_Exports.py
│   └── 13_Methodology.py
├── utils/
│   ├── __init__.py
│   ├── synthetic_data_generator.py # Generates 7 relational realistic datasets
│   └── ui_components.py            # Custom CSS, KPI cards, badges, and dark themes
├── data/                           # Out-of-the-box demo datasets
│   ├── suppliers.csv               # 25 suppliers with ratings & financial risk
│   ├── purchase_orders.csv         # 165 POs spanning 9 months
│   ├── inventory.csv               # 180 material records across 3 plants
│   ├── bill_of_materials.csv       # 90 BOM mappings for 8 finished products
│   ├── production.csv              # 45 production orders with shortage scenarios
│   ├── transportation.csv          # 140 shipments across Air, Ocean, Road, Rail
│   └── demand.csv                  # 288 weekly demand records with volatility spikes
└── tests/
    ├── __init__.py
    └── test_chainguard.py          # 10 automated test cases (100% passing)
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Pip

### 2. Installation
Clone or navigate to the project directory and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Generate or Refresh Synthetic Demo Data (Optional)
The repository includes pre-generated datasets in `data/`. To re-generate fresh datasets with fixed seed:
```bash
python utils/synthetic_data_generator.py
```

### 4. Run Automated Test Suite
Ensure all algorithmic computations, leakage safeguards, and PDF generators pass:
```bash
pytest tests/test_chainguard.py
```

### 5. Launch the Streamlit Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🔒 Zero Target-Leakage & Responsible AI Governance

- **Zero Information Leakage:** In the Disruption Prediction Engine, models are strictly prohibited from consuming post-order placement information (e.g., actual delivery date, arrival timestamps, or received volumes).
- **No Fictitious Data:** In cases where quality ratings or financial risk scores are not present in uploaded user files, the system excludes those sub-indices rather than generating artificial data.
- **Audited Financial Impact:** Costs are strictly segregated between historical outlays, working capital carrying charges, and model-based statistical estimates.
