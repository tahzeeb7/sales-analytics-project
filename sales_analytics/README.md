# Predictive Sales Analytics & Strategy Simulation System
### Final Year Project — Business Intelligence + ML/DL/Agentic AI

---

## Project Overview

A complete end-to-end system that:
- **Predicts** sales revenue and customer churn using ML (Random Forest, XGBoost)
- **Forecasts** time-series sales trends using Deep Learning (LSTM, GRU)
- **Simulates** business strategies with what-if analysis
- **Visualizes** all insights in an interactive BI Dashboard (Streamlit + Plotly)
- **Answers** natural-language strategy questions using an AI Agent (LangChain + GPT-4o-mini)
- **Exposes** predictions via a REST API (FastAPI)

---

## Tech Stack

| Layer              | Technology                                       |
|--------------------|--------------------------------------------------|
| Data Processing    | Python, Pandas, NumPy                            |
| Machine Learning   | Scikit-learn, XGBoost, LightGBM                  |
| Deep Learning      | TensorFlow/Keras (LSTM, GRU)                     |
| Time Series        | ARIMA (pmdarima), statsmodels                    |
| BI Dashboard       | Streamlit, Plotly                                |
| Agentic AI         | LangChain, OpenAI GPT-4o-mini                    |
| REST API           | FastAPI, Uvicorn                                 |
| Reports            | ReportLab, FPDF2, OpenPyXL                       |

---

## Project Structure

```
sales_analytics/
├── data/
│   ├── generate_data.py       # Synthetic data generator
│   └── sales_data.csv         # Generated dataset (after running step 1)
│
├── src/
│   ├── preprocessing.py       # EDA + feature engineering + encoding
│   ├── ml_models.py           # Random Forest, XGBoost training
│   ├── deep_learning.py       # LSTM & GRU time-series models
│   └── api.py                 # FastAPI REST endpoints
│
├── agents/
│   └── strategy_agent.py      # LangChain AI strategy agent
│
├── dashboard/
│   └── app.py                 # Full Streamlit BI dashboard
│
├── models/                    # Saved .pkl model files (auto-created)
├── reports/                   # EDA plots & exports (auto-created)
│
├── run_pipeline.py            # Master orchestration script
├── requirements.txt           # All dependencies
└── .env.template              # Environment variables template
```

---

## Setup & Installation

### 1. Clone / create project folder
```bash
mkdir sales_analytics && cd sales_analytics
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment (optional, for AI Agent)
```bash
cp .env.template .env
# Edit .env and add your OpenAI API key
```

---

## Running the Project

### Step 1 — Generate Data
```bash
python data/generate_data.py
```

### Step 2 — EDA & Preprocessing
```bash
python src/preprocessing.py
```

### Step 3 — Train ML Models (Revenue + Churn)
```bash
python src/ml_models.py
```

### Step 4 — Train Deep Learning Models (LSTM/GRU)
```bash
python src/deep_learning.py
```

### Step 5 — Launch BI Dashboard
```bash
streamlit run dashboard/app.py
# Opens at http://localhost:8501
```

### Step 6 — Launch REST API (optional)
```bash
uvicorn src.api:app --reload --port 8000
# Docs at http://localhost:8000/docs
```

### Step 7 — Run AI Strategy Agent
```bash
python agents/strategy_agent.py
```

### OR run everything at once
```bash
python run_pipeline.py --steps all
```

---

## Dashboard Pages

| Page                 | Features                                                    |
|----------------------|-------------------------------------------------------------|
| Executive Dashboard  | KPIs, revenue trends, pie charts, heatmaps                  |
| Sales Forecasting    | Moving avg + LSTM forecast with confidence intervals        |
| Churn Prediction     | Risk scores, segmentation, single customer predictor        |
| Strategy Simulator   | Discount what-if, regional budget allocator, product mix    |
| AI Strategy Agent    | Chat interface with GPT-4o-mini + real data tools           |
| Reports              | Download CSV, summary stats, export                        |

---

## API Endpoints

| Method | Endpoint                   | Description                  |
|--------|----------------------------|------------------------------|
| GET    | /                          | Health check                 |
| POST   | /predict/revenue           | Predict transaction revenue  |
| POST   | /predict/churn             | Predict customer churn       |
| POST   | /simulate/strategy         | Discount strategy simulation |
| GET    | /analytics/summary         | Overall KPI summary          |
| GET    | /analytics/by-category     | Revenue by product category  |
| GET    | /analytics/by-region       | Revenue by region            |

---

## Project Report Outline (Suggested)

1. Introduction & Problem Statement
2. Literature Review (BI, ML in Sales, LSTM forecasting)
3. System Architecture
4. Data Collection & Preprocessing
5. ML Models — Revenue Prediction & Churn Classification
6. Deep Learning — LSTM/GRU Time-Series Forecasting
7. Agentic AI — LangChain Strategy Agent
8. BI Dashboard Design & Implementation
9. Evaluation & Results
10. Conclusion & Future Work

---

## Dataset Description

Synthetic dataset with **5,000 transactions** spanning 2021–2024.

| Column              | Description                          |
|---------------------|--------------------------------------|
| transaction_id      | Unique transaction ID                |
| date                | Transaction date                     |
| product_category    | Electronics/Clothing/Home Goods/...  |
| region              | North/South/East/West/Central        |
| channel             | Online/Retail Store/Wholesale/...    |
| quantity            | Units sold                           |
| unit_price          | Price per unit                       |
| discount            | Discount applied (0–0.2)             |
| revenue             | Total revenue                        |
| profit              | Profit earned                        |
| customer_churned    | 1 = churned, 0 = retained            |

---

*Built with Python • Scikit-learn • TensorFlow • LangChain • Streamlit • FastAPI*
