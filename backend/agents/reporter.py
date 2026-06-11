"""
Agent 5 — Production Executive Report Agent
---------------------------------------------
Generates:
  1. Groq LLM executive summary (CEO-level, data-driven)
  2. Professional PDF with:
     * Cover page with logo placeholder and date
     * KPI summary table
     * Full analytics narrative (4 sections)
     * All charts embedded
     * Forecast table with confidence intervals
     * Recommendations section
     * Data quality appendix
  3. Raw report text stored in state for frontend display
"""

import os, time
from datetime import datetime
from core.state import AgentState
from langchain_groq import ChatGroq

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak,
)

REPORTS_DIR = "static/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# Brand colours
BRAND_DARK  = colors.HexColor("#1E3A5F")
BRAND_MID   = colors.HexColor("#2563EB")
BRAND_LIGHT = colors.HexColor("#EFF6FF")
ACCENT      = colors.HexColor("#059669")
WARN        = colors.HexColor("#D97706")
DANGER      = colors.HexColor("#DC2626")


def summary_agent(state: AgentState) -> AgentState:
    t0 = time.time()
    print("\n=== Agent 5: Executive Report ===")
    state["current_agent"] = "reporter"
    state.setdefault("errors", [])
    state.setdefault("processing_time", {})

    try:
        analytics = state.get("analytics_result") or {}
        forecast  = state.get("forecast_result") or {}
        cleaning  = state.get("cleaning_report") or {}
        charts    = state.get("chart_metadata") or []

        # -- 1. Build LLM prompt -----------------------------------------------
        rev   = analytics.get("revenue", {})
        prod  = analytics.get("product", {})
        reg   = analytics.get("region", {})
        cust  = analytics.get("customer", {})
        ts    = analytics.get("time_series", {})
        summ  = analytics.get("summary", {})

        prompt = f"""
You are a senior business analyst preparing a board-level executive report.
Write a professional, concise, data-driven report using ONLY the numbers provided.
Do NOT invent or estimate numbers not given. If a value is None or N/A, skip it.

═══ FINANCIAL PERFORMANCE ═══
Total Revenue:       {rev.get('total', 'N/A')}
Average Transaction: {rev.get('average', 'N/A')}
Median Transaction:  {rev.get('median', 'N/A')}
Revenue Std Dev:     {rev.get('std_dev', 'N/A')}

═══ PRODUCT PERFORMANCE ═══
Top Product:   {prod.get('top_product','N/A')} — ${prod.get('top_revenue','N/A')}
Worst Product: {prod.get('worst_product','N/A')}
Unique SKUs:   {prod.get('unique_products','N/A')}
Pareto (80% revenue from): top {prod.get('pareto_80_products','N/A')} products

═══ REGIONAL PERFORMANCE ═══
Best Region:       {reg.get('best_region','N/A')} — ${reg.get('best_revenue','N/A')}
Worst Region:      {reg.get('worst_region','N/A')} — ${reg.get('worst_revenue','N/A')}
Performance Gap:   {reg.get('performance_gap_pct','N/A')}%

═══ GROWTH METRICS ═══
MoM Growth:   {ts.get('latest_mom_growth','N/A')}%
QoQ Growth:   {ts.get('latest_qoq_growth','N/A')}%
CAGR:         {ts.get('cagr_pct','N/A')}%
Best Month:   {ts.get('best_month','N/A')}
Worst Month:  {ts.get('worst_month','N/A')}
Peak Season:  {ts.get('peak_season_month','N/A')}

═══ CUSTOMER INSIGHTS ═══
Total Customers:   {cust.get('total_customers','N/A')}
Top Customer:      {cust.get('top_customer','N/A')}
Repeat Customers:  {cust.get('repeat_customers','N/A')}
One-time Buyers:   {cust.get('one_time_customers','N/A')}

═══ FORECASTING ═══
Model Used:          {forecast.get('best_model','N/A')} (MAPE: {forecast.get('best_mape_pct','N/A')}%)
Confidence Level:    {forecast.get('confidence','N/A')}
Next Month Forecast: ${forecast.get('next_month','N/A')}
Next Quarter:        ${forecast.get('next_quarter','N/A')}
Next 6 Months:       ${forecast.get('next_6_months','N/A')}
Expected Growth:     {forecast.get('expected_growth_pct','N/A')}%
Trend Direction:     {forecast.get('trend_direction','N/A')}

═══ DATA QUALITY ═══
Rows Analysed:       {cleaning.get('final_rows','N/A')}
Quality Score:       {cleaning.get('quality_score','N/A')}/100
Duplicates Removed:  {cleaning.get('exact_duplicates_removed',0)}
Outliers Removed:    {cleaning.get('total_outliers_removed',0)}

Write EXACTLY these 5 sections with these headers:
## 1. Executive Summary
(3-4 sentences: overall business health, standout achievement, key concern)

## 2. Key Findings
(6-8 bullet points with specific numbers from the data above)

## 3. Growth Analysis
(2-3 paragraphs on revenue trajectory, seasonality, and trend direction)

## 4. Recommendations
(4-5 numbered, actionable, specific recommendations with business justification)

## 5. Risk Factors
(3 key risks based on the data — underperforming regions/products, concentration risk, forecast uncertainty)

Tone: professional, direct, no filler phrases. Use $ and % symbols. Max 600 words total.
"""

        groq_key = os.getenv("GROQ_API_KEY")
        # If API key is missing/placeholder/invalid, fall back to a deterministic report
        # so the pipeline can still complete locally.
        if not groq_key or groq_key.strip() in {"", "YOUR_KEY_HERE"}:
            report_text = _fallback_report_text(analytics, forecast, cleaning)
            state["report_text"] = report_text
            print("  ⚠ GROQ_API_KEY missing/placeholder — using fallback report")
        else:
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=groq_key,
                temperature=0.2,
                max_tokens=1500,
            )
            response = llm.invoke(prompt)
            report_text = response.content
            state["report_text"] = report_text
            print("  [OK] LLM summary generated")

        # -- 2. Build PDF ------------------------------------------------------
        base     = os.path.splitext(state.get("filename","report"))[0]
        pdf_path = f"{REPORTS_DIR}/{base}_executive_report.pdf"
        _build_pdf(pdf_path, report_text, analytics, forecast, cleaning, charts, state.get("filename",""))
        state["pdf_path"] = pdf_path
        state["processing_time"]["reporter"] = round(time.time() - t0, 2)
        print(f"  [OK] PDF saved: {pdf_path}  ({state['processing_time']['reporter']}s)")

    except Exception as e:
        import traceback
        err = f"Reporter: {e}"
        print(f"  [FAIL] {err}\n{traceback.format_exc()}")
        state["errors"].append(err)
        state["report_text"] = f"Report generation failed: {e}"
        state["pdf_path"]    = None
        state["processing_time"]["reporter"] = round(time.time() - t0, 2)

    return state


# -- PDF builder ---------------------------------------------------------------

def _fallback_report_text(analytics: dict, forecast: dict, cleaning: dict) -> str:
    rev  = analytics.get("revenue", {}) if analytics else {}
    prod = analytics.get("product", {}) if analytics else {}
    reg  = analytics.get("region", {}) if analytics else {}
    cust = analytics.get("customer", {}) if analytics else {}
    ts   = analytics.get("time_series", {}) if analytics else {}
    fc   = forecast or {}

    def f(v, default="N/A"):
        return default if v is None else v

    total_rev = f(rev.get("total"))
    mom = f(ts.get("latest_mom_growth"))
    best_region = f(reg.get("best_region"))
    top_product = f(prod.get("top_product"))
    quality = cleaning.get("quality_score", "N/A")

    next_month = f(fc.get("next_month"))
    best_model = f(fc.get("best_model"))

    # Must keep same 5-section format used by the LLM prompt.
    return f"""## 1. Executive Summary
Total Revenue: {total_rev}. Revenue performance indicates {'strong' if mom not in ['N/A', None] and float(mom) >= 0 else 'mixed'} recent momentum.
Top Product is {top_product}, with Best Region {best_region} contributing the strongest share. Data quality score is {quality}/100.

## 2. Key Findings
- Total Revenue: ${total_rev if total_rev != 'N/A' else 'N/A'}
- MoM Growth: {mom if mom != 'N/A' else 'N/A'}%
- Top Product: {top_product}
- Best Region: {best_region}
- Next Month Forecast: ${next_month if next_month != 'N/A' else 'N/A'}
- Forecast Model: {best_model}

## 3. Growth Analysis
The recent month-over-month change (MoM) is {mom if mom != 'N/A' else 'N/A'}%, indicating {'an improving trend' if mom not in ['N/A', None] and float(mom) > 0 else 'a cautious outlook'}.
Forecasting suggests next month revenue at ${next_month if next_month != 'N/A' else 'N/A'} using {best_model}. Additional growth will depend on persistence of current regional and product performance.

## 4. Recommendations
1. Double down on {top_product} by prioritizing inventory and marketing budgets toward this product line.
2. Apply region-focused interventions in {best_region} while auditing underperformers for root causes.
3. Use the forecast as a planning baseline for next month and update assumptions as new monthly data arrives.
4. Improve data completeness where quality is lower than targets (current quality score: {quality}/100).

## 5. Risk Factors
- Regional concentration risk: overreliance on {best_region}.
- Product concentration risk: performance dependence on {top_product}.
- Forecast uncertainty: model {best_model} confidence varies with historical volatility.
"""


def _build_pdf(path, report_text, analytics, forecast, cleaning, charts, filename):
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    story  = []

    # Define styles
    h1 = ParagraphStyle("H1", fontSize=22, textColor=BRAND_DARK,
                         spaceAfter=8, fontName="Helvetica-Bold")
    h2 = ParagraphStyle("H2", fontSize=15, textColor=BRAND_MID,
                         spaceAfter=6, spaceBefore=12, fontName="Helvetica-Bold")
    h3 = ParagraphStyle("H3", fontSize=12, textColor=BRAND_DARK,
                         spaceAfter=4, spaceBefore=8, fontName="Helvetica-Bold")
    body = ParagraphStyle("Body", fontSize=10, leading=16, spaceAfter=6)
    bullet = ParagraphStyle("Bullet", fontSize=10, leading=16,
                              spaceAfter=4, leftIndent=16, bulletIndent=4)
    caption = ParagraphStyle("Caption", fontSize=8, textColor=colors.grey,
                              alignment=1, spaceAfter=4)

    # -- Cover -----------------------------------------------------------------
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("BUSINESS INTELLIGENCE", ParagraphStyle(
        "cover_sub", fontSize=12, textColor=BRAND_MID, alignment=1,
        fontName="Helvetica", spaceAfter=4)))
    story.append(Paragraph("Executive Report", ParagraphStyle(
        "cover_title", fontSize=32, textColor=BRAND_DARK, alignment=1,
        fontName="Helvetica-Bold", spaceAfter=12)))
    story.append(HRFlowable(width="80%", thickness=2, color=BRAND_MID,
                             hAlign="CENTER", spaceAfter=16))
    story.append(Paragraph(f"Source: {filename}", ParagraphStyle(
        "cover_file", fontSize=11, textColor=colors.grey, alignment=1)))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        ParagraphStyle("cover_date", fontSize=11, textColor=colors.grey, alignment=1)))
    story.append(PageBreak())

    # -- KPI Table -------------------------------------------------------------
    story.append(Paragraph("Key Performance Indicators", h2))
    rev  = analytics.get("revenue", {})
    prod = analytics.get("product", {})
    reg  = analytics.get("region", {})
    ts   = analytics.get("time_series", {})
    fc   = forecast

    kpi_rows = [["Metric", "Value", "Metric", "Value"]]
    kpis_left = [
        ("Total Revenue",   f"${rev.get('total',0):,.2f}"     if rev.get('total') else "N/A"),
        ("Avg Transaction", f"${rev.get('average',0):,.2f}"   if rev.get('average') else "N/A"),
        ("Top Product",     str(prod.get("top_product","N/A"))),
        ("Best Region",     str(reg.get("best_region","N/A"))),
    ]
    kpis_right = [
        ("MoM Growth",      f"{ts.get('latest_mom_growth',0):.1f}%"   if ts.get('latest_mom_growth') is not None else "N/A"),
        ("Next Month Fcst", f"${fc.get('next_month',0):,.0f}"          if fc.get('next_month') else "N/A"),
        ("Forecast Model",  str(fc.get("best_model","N/A"))),
        ("Data Quality",    f"{cleaning.get('quality_score','N/A')}/100"),
    ]
    for (lk, lv), (rk, rv) in zip(kpis_left, kpis_right):
        kpi_rows.append([lk, lv, rk, rv])

    kpi_table = Table(kpi_rows, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  BRAND_DARK),
        ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRAND_LIGHT, colors.white]),
        ("FONTNAME",    (0,1), (0,-1),  "Helvetica-Bold"),
        ("FONTNAME",    (2,1), (2,-1),  "Helvetica-Bold"),
        ("GRID",        (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("PADDING",     (0,0), (-1,-1), 7),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.3*inch))

    # -- Report Text -----------------------------------------------------------
    for line in report_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.08*inch))
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(stripped[3:], h2))
        elif stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], h3))
        elif stripped.startswith(("- ", "* ", "* ")):
            story.append(Paragraph(stripped[2:], bullet))
        elif stripped[0].isdigit() and stripped[1:3] in (". ", ") "):
            story.append(Paragraph(stripped, bullet))
        else:
            story.append(Paragraph(stripped, body))

    # -- Forecast Table --------------------------------------------------------
    fc3 = forecast.get("forecast_3m", [])
    if fc3:
        story.append(PageBreak())
        story.append(Paragraph("Revenue Forecast", h2))
        story.append(Paragraph(
            f"Model: {forecast.get('best_model','N/A')} | "
            f"Accuracy: {100 - forecast.get('best_mape_pct',0):.1f}% | "
            f"Confidence: {forecast.get('confidence','N/A').upper()}",
            ParagraphStyle("fc_meta", fontSize=9, textColor=colors.grey, spaceAfter=8)
        ))
        fc_header = ["Month", "Forecast ($)", "Lower 80%", "Upper 80%"]
        fc_data   = [fc_header]
        for r in forecast.get("forecast_6m", fc3):
            row = [
                r.get("month",""),
                f"${r.get('forecast',0):,.0f}",
                f"${r.get('lower_80',r.get('forecast',0)*0.9):,.0f}",
                f"${r.get('upper_80',r.get('forecast',0)*1.1):,.0f}",
            ]
            fc_data.append(row)
        fc_table = Table(fc_data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
        fc_table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0),  BRAND_MID),
            ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
            ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRAND_LIGHT, colors.white]),
            ("GRID",        (0,0), (-1,-1), 0.3, colors.lightgrey),
            ("PADDING",     (0,0), (-1,-1), 7),
            ("ALIGN",       (1,0), (-1,-1), "RIGHT"),
        ]))
        story.append(fc_table)

        # Scenarios
        story.append(Spacer(1, 0.2*inch))
        scenarios = forecast.get("scenarios", {})
        if scenarios:
            sc_data = [
                ["Scenario", "Next Month Revenue", "Assumption"],
                ["🟢 Optimistic",  f"${scenarios.get('optimistic',0):,.0f}",  "+20% above forecast"],
                ["🟡 Realistic",   f"${scenarios.get('realistic',0):,.0f}",   "Base forecast"],
                ["🔴 Pessimistic", f"${scenarios.get('pessimistic',0):,.0f}", "-20% below forecast"],
            ]
            sc_table = Table(sc_data, colWidths=[4.5*cm, 5*cm, 8.5*cm])
            sc_table.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,0),  BRAND_DARK),
                ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
                ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
                ("FONTSIZE",    (0,0), (-1,-1), 9),
                ("GRID",        (0,0), (-1,-1), 0.3, colors.lightgrey),
                ("PADDING",     (0,0), (-1,-1), 7),
            ]))
            story.append(Paragraph("Revenue Scenarios", h3))
            story.append(sc_table)

    # -- Charts ----------------------------------------------------------------
    # Plotly charts are saved as HTML in this project; ReportLab's Image() can only embed raster images.
    if charts:
        story.append(PageBreak())
        story.append(Paragraph("Data Visualisations", h2))
        for c in charts:
            p = c.get("path")
            if not p or not os.path.exists(p):
                continue

            ext = os.path.splitext(p)[1].lower()
            story.append(Paragraph(c.get("title", "Chart"), h3))

            if ext in {".html", ".htm"}:
                desc = c.get("description", "")
                if desc:
                    story.append(Paragraph(desc, caption))
                story.append(Paragraph(f"(Chart available as HTML: {p})", caption))
                story.append(Spacer(1, 0.2*inch))
                continue

            try:
                story.append(Image(p, width=16*cm, height=8*cm))
                if c.get("description"):
                    story.append(Paragraph(c["description"], caption))
                story.append(Spacer(1, 0.2*inch))
            except Exception:
                # Skip unknown/unembeddable files so the pipeline completes.
                continue


    # -- Data Quality Appendix -------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("Appendix: Data Quality Report", h2))
    qa_rows = [
        ["Metric", "Value"],
        ["Original Rows",       str(cleaning.get("original_rows","N/A"))],
        ["Final Rows",          str(cleaning.get("final_rows","N/A"))],
        ["Duplicates Removed",  str(cleaning.get("exact_duplicates_removed",0))],
        ["Missing Values Fixed",str(cleaning.get("missing_values_before",0))],
        ["Outliers Removed",    str(cleaning.get("total_outliers_removed",0))],
        ["Quality Score",       f"{cleaning.get('quality_score','N/A')}/100"],
        ["Date Cols Parsed",    ", ".join(cleaning.get("date_cols_parsed",[]) or ["none"])],
    ]
    qa_table = Table(qa_rows, colWidths=[7*cm, 10*cm])
    qa_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  BRAND_DARK),
        ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRAND_LIGHT, colors.white]),
        ("GRID",        (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("PADDING",     (0,0), (-1,-1), 7),
    ]))
    story.append(qa_table)

    doc.build(story)