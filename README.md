# 🤖 BI Platform — Multi-Agent Business Intelligence

> Enterprise-grade AI analytics platform powered by 5 specialized LangGraph agents. Upload any business data file and get a complete executive analysis in under 60 seconds.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16+-black?style=flat&logo=next.js&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B35?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?style=flat&logo=postgresql&logoColor=white)

---

## 🎯 What It Does

Companies have sales, marketing, and finance data in CSV/Excel files. Managers want answers like:

- Why did sales drop last month?
- Which product generates maximum profit?
- What will revenue be next quarter?
- Which customers are likely to churn?

**This platform answers all of it in under 20 seconds — automatically.**

---

## 🏗️ Architecture

```
Frontend (Next.js + Tailwind)
         ↓
FastAPI Backend
         ↓
LangGraph Multi-Agent Pipeline
         ↓
┌─────────────────────────────┐
│  Agent 1: Data Cleaning     │  Pandas, NumPy
│  Agent 2: Analytics         │  Pandas SQL, Statistics
│  Agent 3: Visualization     │  Plotly (10 charts)
│  Agent 4: Forecasting       │  Prophet, XGBoost, ARIMA
│  Agent 5: Executive Report  │  Groq LLM + ReportLab PDF
└─────────────────────────────┘
         ↓
Neon PostgreSQL (job history)
         ↓
Groq LLM (Llama 3.3 70B)
```

---

## ✨ Features

### AI Agent Pipeline
- **Agent 1 — Data Cleaning**: Auto-detects encoding, removes duplicates, fills nulls, removes outliers, converts currency strings, parses dates — gives quality score 0-100
- **Agent 2 — Analytics**: Revenue KPIs, product/region/customer analysis, MoM/QoQ/CAGR growth, anomaly detection, correlation matrix, Pareto analysis
- **Agent 3 — Visualization**: 10 production charts — bar, line, donut, heatmap, scatter, anomaly detection
- **Agent 4 — Forecasting**: Tries Prophet → XGBoost → ARIMA → Linear Regression, picks best by MAPE, gives 6-month forecast with scenarios
- **Agent 5 — Executive Report**: CEO-level LLM report + multi-page PDF with KPI table, charts, forecast scenarios

### Supported File Formats
CSV · TSV · Excel (xlsx/xls/xlsm/ods) · JSON · JSONL · Parquet · XML · ZIP

### Production Stack
| Layer | Technology |
|---|---|
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| AI Agents | LangGraph, LangChain |
| LLM | Groq (Llama 3.3 70B) — free tier |
| Forecasting | Prophet, XGBoost, ARIMA, Scikit-learn |
| Database | Neon PostgreSQL |
| Auth | Clerk (Google, GitHub, Email) |
| Charts | Plotly + Kaleido |
| PDF | ReportLab |
| Deploy | Vercel (FE) + Render (BE) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Neon PostgreSQL (free at [neon.tech](https://neon.tech))
- Clerk account (free at [clerk.com](https://clerk.com))

### Backend Setup

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/bi-platform.git
cd bi-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GROQ_API_KEY and DATABASE_URL

# Run backend
uvicorn main:app --reload
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd bi-platform/frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local
# Add your Clerk keys and API URL

# Run frontend
npm run dev
# App running at http://localhost:3000
```

### Environment Variables

**backend/.env**
```
GROQ_API_KEY=your_groq_key_here
DATABASE_URL=postgresql://user:pass@host/dbname
```

**frontend/.env.local**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
```

---

## 📊 Dashboard Preview

| Section | Description |
|---|---|
| **Upload Zone** | Drag & drop any CSV/Excel/JSON file |
| **Live Progress** | Watch all 5 agents run in real-time |
| **8 KPI Cards** | Revenue, growth, forecast, quality score |
| **Analytics Tables** | Products, Regions, Customers, Time Series |
| **10 Charts** | Bar, line, donut, heatmap, scatter, anomaly |
| **Executive Report** | AI-written CEO summary with 5 sections |
| **PDF Download** | Full multi-page report with charts |

---

# 📸 Screenshots

## Landing Page

The platform provides a clean AI-powered Business Intelligence interface where users can upload datasets and launch a complete analytics pipeline.

![Landing Page](screenshots/landing-page.png)

---

## Executive Dashboard

After analysis completes, the platform generates KPI cards, growth metrics, forecasts, and business insights automatically.

![Executive Dashboard](screenshots/dashboard-overview.png)

---

## Product Analytics

Identify top-performing products, revenue contribution, transaction volume, and Pareto distribution.

![Product Analytics](screenshots/product-analysis.png)

---

## Regional Performance Analysis

Compare performance across regions and identify best and worst performing markets.

![Regional Analytics](screenshots/region-analysis.png)

---

## Customer Intelligence

Discover high-value customers, repeat buyers, customer concentration, and revenue distribution.

![Customer Analytics](screenshots/customer-analysis.png)

---

## Time-Series Analysis

Track monthly trends, growth rates, anomalies, and seasonality.

![Time Series Analytics](screenshots/time-series-analysis.png)

---

## Visualization Engine

The platform automatically generates 10 business intelligence charts including revenue trends, customer insights, heatmaps, anomaly detection, and forecasting visualizations.

![Charts](screenshots/charts-grid.png)

---

## Forecasting Module

Four forecasting models are evaluated automatically and the best model is selected using MAPE.

Models:
- Prophet
- XGBoost
- ARIMA
- Linear Regression

![Forecasting](screenshots/forecast-analysis.png)

---

## Data Quality Assessment

The Data Cleaning Agent performs automated quality checks and generates a detailed quality report.

![Data Quality](screenshots/data-quality.png)

---

## AI Executive Report

The Groq-powered Executive Report Agent generates an executive-level business report with actionable recommendations and risk analysis.

![Executive Report](screenshots/executive-report.png)

---

## PDF Export

Generate a downloadable multi-page PDF report suitable for managers, stakeholders, and executives.

✔ KPI Summary

✔ Forecast Results

✔ Data Quality Assessment

✔ Strategic Recommendations

✔ Risk Analysis


## 🔬 Agent Performance (on test_sales.csv)

```
Agent 1 — Cleaner     : 0.05s
Agent 2 — Analytics   : 0.02s
Agent 3 — Visualizer  : 3.00s   (10 charts)
Agent 4 — Forecaster  : 7.00s   (4 ML models)
Agent 5 — Reporter    : 4.00s   (LLM + PDF)
──────────────────────────────
Total                 : ~14s
```

---

## 📁 Project Structure

```
bi-platform/
├── backend/
│   ├── agents/
│   │   ├── cleaner.py       # Data cleaning agent
│   │   ├── analytics.py     # Analytics agent
│   │   ├── visualizer.py    # Visualization agent
│   │   ├── forecaster.py    # Forecasting agent
│   │   └── reporter.py      # Executive report agent
│   ├── core/
│   │   ├── state.py         # LangGraph shared state
│   │   └── graph.py         # Pipeline wiring
│   ├── routes/
│   │   └── analyze.py       # FastAPI endpoints
│   ├── utils/
│   │   └── file_loader.py   # Multi-format file loader
│   ├── database.py          # Neon PostgreSQL models
│   └── main.py              # FastAPI app entry point
└── frontend/
    ├── app/
    │   ├── page.tsx         # Main dashboard
    │   ├── sign-in/         # Clerk auth pages
    │   └── sign-up/
    ├── components/
    │   ├── Navbar.tsx
    │   ├── FileUpload.tsx
    │   ├── AgentProgress.tsx
    │   ├── KPICards.tsx
    │   ├── ChartGrid.tsx
    │   ├── AnalyticsTables.tsx
    │   └── ReportPanel.tsx
    ├── hooks/
    │   └── usePipeline.ts   # Upload + polling hook
    ├── lib/
    │   └── api.ts           # API utility functions
    └── types/
        └── index.ts         # TypeScript types
```

---

## 🌐 Deployment

| Service | Platform | URL |
|---|---|---|
| Frontend | Vercel | `https://bi-platform.vercel.app` |
| Backend | Render | `https://bi-platform-api.onrender.com` |
| Database | Neon | PostgreSQL cloud |
| Auth | Clerk | OAuth + email |

---

## 📝 Resume Description

> Developed an enterprise-grade Multi-Agent Business Intelligence Platform using LangGraph, FastAPI, Next.js, and PostgreSQL. Designed 5 collaborating AI agents for automated data cleaning, analytics, visualization, ML forecasting (Prophet/XGBoost/ARIMA), and executive report generation. Implemented natural-language business insights, 10 dynamic charts, predictive revenue forecasting with confidence intervals, and automated PDF report generation. Built with Clerk authentication, Neon PostgreSQL persistence, and deployed on Vercel + Render.

---

## 🛠️ Tech Stack Summary

**AI/ML**: LangGraph · LangChain · Groq (Llama 3.3 70B) · Prophet · XGBoost · ARIMA · Scikit-learn

**Backend**: FastAPI · Python 3.11 · SQLAlchemy · Pandas · NumPy · Plotly · ReportLab

**Frontend**: Next.js 16 · TypeScript · Tailwind CSS · Clerk Auth

**Infrastructure**: Neon PostgreSQL · Vercel · Render · GitHub

---

## 📄 License

MIT License — free to use for portfolio and commercial projects.

---

*Built with ❤️ using LangGraph + Groq + Next.js*
