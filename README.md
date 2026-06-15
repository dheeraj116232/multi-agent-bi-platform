# 🤖 Multi-Agent BI Platform

> Enterprise-grade Business Intelligence platform powered by 5 specialized LangGraph AI agents. Upload any business data file and receive a complete executive analysis — cleaned data, deep analytics, 10 charts, ML-based forecasts, and a CEO-ready PDF report — in under 30 seconds.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat&logo=next.js&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B35?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?style=flat&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**🔗 Live Demo:** [multi-agent-bi-platform.vercel.app](https://multi-agent-bi-platform.vercel.app)
**🔗 API Docs:** [multi-agent-bi-platform.onrender.com/docs](https://multi-agent-bi-platform.onrender.com/docs)

---

## 📸 Demo

<!-- Add a screenshot of your dashboard here -->
<img width="1896" height="1002" alt="image" src="https://github.com/user-attachments/assets/e912df79-e02e-45a6-83ca-a2fdc6c38114" />

<!-- ![Dashboard Screenshot](./docs/screenshot-dashboard.png) -->
<img width="948" height="500" alt="image" src="https://github.com/user-attachments/assets/ed482018-7c57-48ef-8208-6021b94e33a3" />
<img width="948" height="997" alt="image" src="https://github.com/user-attachments/assets/293d2352-6900-4563-a285-d8fabd798bbb" />
<img width="948" height="930" alt="image" src="https://github.com/user-attachments/assets/a85e2673-0501-4415-b501-ca8c6972635a" />
<img width="948" height="927" alt="image" src="https://github.com/user-attachments/assets/75b0ff6f-dfff-40c6-b4bb-288686021849" />
<img width="948" height="736" alt="image" src="https://github.com/user-attachments/assets/34c53fae-6636-478a-ae27-f0c3cebb6c50" />
<img width="948" height="765" alt="image" src="https://github.com/user-attachments/assets/5ee12d1c-d864-41a3-a8e2-5470efa375ee" />
<img width="948" height="850" alt="image" src="https://github.com/user-attachments/assets/fd36de05-834c-43b5-8d68-7e521d4dd56c" />
<img width="948" height="706" alt="image" src="https://github.com/user-attachments/assets/ca1db378-432f-4907-b24b-06819b900afe" />









<!-- Add a short demo video/GIF here -->
Project Demo Video -- https://youtu.be/HEzumIojwzQ
<!-- ![Demo](./docs/demo.gif) -->

> See [📷 Screenshots & Demo Video](#-screenshots--demo-video) for upload instructions.

---

## 🎯 The Problem

Companies sit on mountains of sales, marketing, and finance data in spreadsheets. Managers ask questions like:

- Why did revenue drop last month?
- Which product drives the most profit?
- What will next quarter's revenue look like?
- Which region and customers need attention?

Normally, an analyst spends hours pulling this together manually. **This platform does it in under 30 seconds — fully automated.**

---

## 🏗️ Architecture

```mermaid
graph TD
    A[User uploads CSV/Excel/JSON] --> B[FastAPI /api/analyze]
    B --> C[Agent 1: Data Cleaning]
    C --> D[Agent 2: Analytics]
    D --> E[Agent 3: Visualization - Matplotlib]
    E --> F[Agent 4: Forecasting - Prophet/XGBoost/ARIMA]
    F --> G[Agent 5: Executive Report - Groq LLM + PDF]
    G --> H[Next.js Dashboard]
    H --> I[KPI Cards + Charts + Tables]
    H --> J[Download PDF Report]
    G --> K[(Neon PostgreSQL - job history)]
    B -. progress polling .-> H
```

Each agent receives a shared `AgentState` object, performs its task, and passes the enriched state to the next node — a fully sequential LangGraph state machine with error isolation per agent (a failure in one agent doesn't crash the pipeline).

---

## ✨ Agent Pipeline in Detail

### 1️⃣ Data Cleaning Agent
- Loads CSV, TSV, Excel (xlsx/xls/xlsm/ods), JSON, JSONL, Parquet, XML, or ZIP
- Auto-detects file encoding
- Removes exact and near-duplicate rows
- Fills missing values (median for numeric, mode for categorical, forward-fill for dates)
- Converts currency strings (`$1,200.50` → `1200.50`)
- Parses date columns automatically across 14+ formats
- Removes statistical outliers (IQR method)
- Detects column roles automatically (revenue, quantity, product, region, customer, date)
- Outputs a **data quality score (0–100)**

### 2️⃣ Analytics Agent
- Revenue KPIs: total, average, median, std deviation
- Product analysis: top/bottom performers, revenue share, Pareto (80/20) analysis
- Regional analysis: best/worst region, performance gap
- Time-series analysis: MoM, QoQ growth, CAGR, seasonality, anomaly detection
- Customer analysis: top customers, repeat vs one-time buyers
- Correlation matrix across all numeric columns

### 3️⃣ Visualization Agent
Generates **10 charts** with Matplotlib (server-safe, no browser dependencies):
1. Revenue by Product (bar)
2. Monthly Revenue Trend + MoM Growth (line + bar overlay)
3. Revenue by Region (bar)
4. Quarterly Revenue (bar)
5. Revenue Share by Product (donut)
6. Top 10 Customers (bar)
7. Correlation Heatmap
8. KPI Dashboard (summary cards)
9. Revenue vs Quantity (bubble scatter)
10. Anomaly Detection (line + markers)

### 4️⃣ Forecasting Agent
Trains **four models** and automatically selects the best by MAPE:
- Prophet (seasonality-aware)
- XGBoost (lag-feature regression)
- ARIMA (auto-order selection)
- Linear Regression (polynomial fallback)

Outputs 3-month and 6-month forecasts with confidence levels and optimistic/realistic/pessimistic scenarios.

### 5️⃣ Executive Report Agent
- Sends structured analytics to **Groq (Llama 3.3 70B)** to generate a 5-section CEO report (Executive Summary, Key Findings, Growth Analysis, Recommendations, Risk Factors)
- Builds a multi-page **PDF** with ReportLab: cover page, KPI table, narrative, forecast table, embedded charts, and data-quality appendix

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.11 |
| **Orchestration** | LangGraph, LangChain |
| **LLM** | Groq — Llama 3.3 70B (free tier) |
| **Forecasting** | Prophet, XGBoost, ARIMA (statsmodels), scikit-learn |
| **Visualization** | Matplotlib (PNG, server-rendered) |
| **PDF Generation** | ReportLab |
| **Database** | Neon Serverless PostgreSQL |
| **Deployment** | Vercel (frontend) · Render (backend) |

---

## 📦 Supported File Formats

`.csv` · `.tsv` · `.xlsx` · `.xls` · `.xlsm` · `.ods` · `.json` · `.jsonl` · `.parquet` · `.xml` · `.zip`

---

## 🧩 Engineering Challenges & Solutions

Real problems hit during development — and how they were solved:

| Challenge | Problem | Solution |
|---|---|---|
| **Chart rendering on serverless** | Plotly's `kaleido` export requires a headless Chrome binary, which is unavailable on Render's free tier — charts silently fell back to unusable HTML files | Rebuilt the entire visualization agent on **Matplotlib's `Agg` backend**, which renders PNGs purely in-process with zero browser dependency |
| **Inconsistent source data** | Real-world CSVs mix currency symbols (`$1,200.50`), 14+ date formats, inconsistent column names, and duplicate/near-duplicate rows | Built a dedicated cleaning agent with regex-based currency parsing, multi-format date inference, column-role detection, and IQR-based outlier removal — outputs a 0–100 data quality score |
| **Forecast reliability on small datasets** | Prophet performs poorly (MAPE > 200%) on datasets with fewer than ~12 months of history | Implemented a **4-model ensemble** (Prophet, XGBoost, ARIMA, Linear Regression) that back-tests each model on a holdout split and automatically selects the lowest-MAPE model per dataset |
| **Long-running pipeline vs HTTP timeouts** | The full 5-agent pipeline takes 15–30 seconds — too long for a synchronous HTTP response | Implemented an async **job-queue pattern**: `/api/analyze` returns a `job_id` instantly, the pipeline runs in a FastAPI background task, and the frontend polls `/api/status/{job_id}` every 2 seconds with live per-agent progress |
| **CORS across split deployments** | Frontend (Vercel) and backend (Render) live on different origins, causing browser-blocked requests | Configured FastAPI `CORSMiddleware` with explicit allowed origins and verified preflight handling for both local and production domains |
| **State management across agents** | Each agent needs access to outputs from all previous agents without tight coupling | Designed a single shared `AgentState` TypedDict passed through a LangGraph `StateGraph`, with per-agent error isolation so one agent's failure doesn't crash the pipeline |

---

## 💼 Business Impact

This isn't just a technical demo — it solves a real operational cost problem:

- **Time savings**: A task that takes a data analyst 2–4 hours (cleaning data, building charts, writing a summary, forecasting next quarter) is reduced to **under 30 seconds**
- **Cost reduction**: At an estimated analyst rate of $30–50/hour, automating a single weekly report saves **$120–200/week per report**, or **$6,000–10,000/year** per recurring report
- **Decision speed**: Executives get same-day answers to "why did revenue drop" instead of waiting for the next scheduled BI cycle
- **Accessibility**: Non-technical managers can self-serve insights without writing a single SQL query or Excel formula
- **Consistency**: Every report follows the same rigorous cleaning → analysis → forecasting → narrative structure, removing analyst-to-analyst variance in report quality

---

## 📈 Scalability

How this architecture grows from a portfolio project to production load:

| Concern | Current State | Scale Path |
|---|---|---|
| **Compute** | Single Render web service, synchronous background tasks | Move agent execution to a dedicated worker pool (Celery/RQ + Redis) so the API stays responsive under concurrent uploads |
| **File storage** | Charts/PDFs written to local disk on the web server | Move to object storage (S3 / Cloudflare R2) so generated assets survive deploys and scale horizontally |
| **Database** | Neon serverless Postgres (auto-scaling, branching) | Already production-ready; add read replicas and connection pooling (PgBouncer) for high concurrency |
| **LLM throughput** | Single Groq API key, sequential calls | Add request batching/queueing and a fallback provider (e.g. OpenAI/Gemini) for rate-limit resilience |
| **Forecasting cost** | 4 models trained per request (CPU-bound) | Cache trained models per dataset hash; only retrain on new data uploads |
| **Multi-tenancy** | Single-user, no auth | Add auth (Clerk/Auth0) + row-level security in Postgres so each user/org only sees their own jobs |
| **Observability** | Print-based logging | Add structured logging (e.g. structlog) + APM (Sentry/Datadog) for production error tracking |

The LangGraph pipeline design means **new agents can be added as new graph nodes** without touching existing agent code — e.g., a "Slack notification agent" or "Email digest agent" can be appended to the end of the graph in a few lines.

---

## 🚀 Future Enterprise Features

Planned enhancements that would make this enterprise-ready:

- **Authentication & multi-tenancy** — per-user/org login, saved analysis history, role-based access (Clerk/Auth0)
- **Natural-language "Chat with your data"** — a 6th agent that answers follow-up questions against the cleaned dataset using RAG over the analytics output
- **Scheduled & recurring reports** — cron-based pipeline runs with email/Slack delivery of the executive PDF
- **Multi-file comparison** — upload two periods (e.g. Q1 vs Q2) and get a comparative delta report
- **Data source connectors** — direct ingestion from Google Sheets, Salesforce, Shopify, and Stripe APIs (no manual file export)
- **Custom branding** — white-label PDF reports with company logo, colors, and custom KPI definitions
- **Alerting** — proactive notifications when anomalies or threshold breaches are detected in new data
- **Export to BI tools** — push cleaned data + analytics into Power BI / Looker / Tableau via API
- **Audit trail** — full versioned history of every report generated, with diffing between runs

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Free [Groq API key](https://console.groq.com)
- Free [Neon PostgreSQL](https://neon.tech) database

### Backend

```bash
git clone https://github.com/dheeraj116232/multi-agent-bi-platform.git
cd multi-agent-bi-platform/backend

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate      # macOS/Linux

pip install -r requirements.txt
```

Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_key_here
DATABASE_URL=postgresql://user:pass@host/dbname
```

Run:
```bash
uvicorn main:app --reload
```
API live at `http://localhost:8000` · Swagger docs at `http://localhost:8000/docs`

### Frontend

```bash
cd ../frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run:
```bash
npm run dev
```
App live at `http://localhost:3000`

---

## 📁 Project Structure

```
multi-agent-bi-platform/
├── backend/
│   ├── agents/
│   │   ├── cleaner.py        # Agent 1 — Data Cleaning
│   │   ├── analytics.py      # Agent 2 — Analytics
│   │   ├── visualizer.py     # Agent 3 — Visualization (Matplotlib)
│   │   ├── forecaster.py     # Agent 4 — Forecasting
│   │   └── reporter.py       # Agent 5 — Executive Report
│   ├── core/
│   │   ├── state.py          # Shared LangGraph state
│   │   └── graph.py          # Pipeline definition
│   ├── routes/
│   │   └── analyze.py        # FastAPI endpoints
│   ├── utils/
│   │   └── file_loader.py    # Multi-format file loader
│   ├── database.py           # SQLAlchemy models (Neon)
│   ├── main.py                # FastAPI entry point
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main dashboard
│   │   └── globals.css
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── FileUpload.tsx
│   │   ├── AgentProgress.tsx
│   │   ├── KPICards.tsx
│   │   ├── ChartGrid.tsx
│   │   ├── AnalyticsTables.tsx
│   │   └── ReportPanel.tsx
│   ├── hooks/
│   │   └── usePipeline.ts     # Upload + status polling
│   ├── lib/
│   │   └── api.ts
│   └── types/
│       └── index.ts
│
├── docs/                       # ← put screenshots/demo video here
│   ├── screenshot-dashboard.png
│   ├── screenshot-charts.png
│   ├── screenshot-report.png
│   └── demo.mp4 / demo.gif
│
├── LICENSE
└── README.md
```

---

## 📷 Screenshots & Demo Video

To add visuals to this README:

1. Create a `docs/` folder at the root of your repo:
   ```bash
   cd C:\Users\niraj\bi-platform
   mkdir docs
   ```

2. Take screenshots of:
   - The upload screen / hero section
   - The KPI cards + analytics tables (full dashboard)
   - The charts grid
   - The executive report panel
   - The downloaded PDF

3. Save them into `docs/` as:
   ```
   docs/screenshot-dashboard.png
   docs/screenshot-charts.png
   docs/screenshot-report.png
   ```

4. For a demo video:
   - Record a 1–2 minute screen recording (Windows: `Win + Alt + R`, or use [ScreenToGif](https://www.screentogif.com/) for a GIF)
   - Save as `docs/demo.mp4` (GitHub renders mp4 inline) or `docs/demo.gif`
   - **GitHub file size limit is 25MB** for files added via web upload, 100MB via git — compress if needed (e.g. with [HandBrake](https://handbrake.fr/))

5. Reference them at the top of this README (uncomment the lines in the **Demo** section):
   ```markdown
   ![Dashboard Screenshot](./docs/screenshot-dashboard.png)
   ![Demo](./docs/demo.gif)
   ```

6. Commit and push:
   ```bash
   git add docs/
   git commit -m "docs: add screenshots and demo video"
   git push origin main
   ```

> **Tip:** For best results on GitHub, keep screenshots under 1MB each (PNG, ~1200px wide) and demo GIFs under 10MB.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Upload a file, returns `job_id` |
| `GET` | `/api/status/{job_id}` | Poll pipeline progress + results |
| `GET` | `/api/chart/{job_id}/{index}` | Fetch a generated chart (PNG) |
| `GET` | `/api/download/pdf/{job_id}` | Download the executive PDF report |
| `GET` | `/api/jobs` | List recent analysis jobs |
| `GET` | `/health` | Health check |

Full interactive docs available at `/docs` (Swagger UI).

---

## 📊 Sample Output

On a 36-row sales dataset:

| Metric | Result |
|---|---|
| Total Revenue | $40,980 |
| Top Product | Laptop ($21.2K · 51.7% share) |
| Best Region | North ($11.6K) |
| MoM Growth | -14.89% |
| QoQ Growth | +24.75% |
| Forecast Model | XGBoost (MAPE 15.3%) |
| Next Month Forecast | $3.1K |
| Data Quality Score | 90 / 100 |
| Charts Generated | 10 |
| Total Pipeline Time | ~15–28s |

---

## 📄 License

MIT License — free to use for portfolio, learning, and commercial projects. See [LICENSE](./LICENSE) for details.

---

*Built with LangGraph · Groq · FastAPI · Next.js*
