"""
Agent 3 — Production Visualization Agent
------------------------------------------
Charts generated (adaptive — only created when underlying data exists):
  1.  Revenue by Product — horizontal bar (top 10)
  2.  Monthly Revenue Trend — line with markers + MoM growth overlay
  3.  Revenue by Region — choropleth-style bar (sorted)
  4.  Quarterly Revenue — grouped bar
  5.  Revenue Share — donut chart (top 8 products)
  6.  Customer Revenue Concentration — bar (top 10 customers)
  7.  Correlation Heatmap — numeric columns
  8.  KPI Summary Card — table / annotation figure
  9.  Sales vs Quantity Scatter — if both columns exist
 10.  Anomaly Highlight — monthly line with anomaly markers

All charts:
  * Consistent corporate colour palette
  * Transparent backgrounds (web-ready)
  * 1200x600 px PNG output (retina-friendly)
  * Saved to static/charts/
"""

import os, time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.state import AgentState

CHARTS_DIR = "static/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# Corporate palette
PALETTE = ["#2563EB","#7C3AED","#059669","#D97706","#DC2626",
           "#0891B2","#65A30D","#DB2777","#EA580C","#4F46E5"]
BG   = "rgba(0,0,0,0)"
GRID = "rgba(100,100,100,0.1)"


def visualization_agent(state: AgentState) -> AgentState:
    t0 = time.time()
    print("\n=== Agent 3: Visualization ===")
    state["current_agent"] = "visualizer"
    state.setdefault("errors", [])
    state.setdefault("processing_time", {})

    chart_paths = []
    chart_meta  = []

    try:
        df        = state["clean_df"]
        analytics = state["analytics_result"] or {}
        col_map   = state.get("column_map") or {}
        base      = os.path.splitext(state.get("filename", "file"))[0]

        if df is None or analytics.get("status") == "failed":
            raise ValueError("Cannot visualise: missing clean data or failed analytics")

        revenue_col  = _first(col_map, "revenue")
        qty_col      = _first(col_map, "quantity")
        product_col  = _first(col_map, "product")
        region_col   = _first(col_map, "region")
        date_col     = _first(col_map, "date")
        customer_col = _first(col_map, "customer")

        def save(fig, name: str, title: str, description: str):
            """Save figure as PNG using kaleido."""
            fig.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(family="Inter, Arial, sans-serif", size=13),
                margin=dict(l=60, r=40, t=60, b=60),
            )
            path = f"{CHARTS_DIR}/{base}_{name}.png"
            try:
                fig.write_image(path, width=1200, height=600, scale=1.5)
                chart_paths.append(path)
                chart_meta.append({
                    "path": path,
                    "title": title,
                    "description": description,
                    "format": "png"
                })
                print(f"  [OK] {title}")
            except Exception as img_err:
                # Fallback to HTML if kaleido fails
                print(f"  [WARN] PNG failed for {title}: {img_err} — saving HTML")
                html_path = f"{CHARTS_DIR}/{base}_{name}.html"
                fig.write_html(html_path)
                chart_paths.append(html_path)
                chart_meta.append({
                    "path": html_path,
                    "title": title,
                    "description": description,
                    "format": "html"
                })

        # ── 1. Product Revenue Bar ────────────────────────────────────────────
        prod_data = analytics.get("product", {}).get("top_10")
        if prod_data and product_col and revenue_col:
            pdf = pd.DataFrame(prod_data).sort_values("total_revenue")
            fig = px.bar(
                pdf, y=product_col, x="total_revenue",
                orientation="h", color="total_revenue",
                color_continuous_scale=["#DBEAFE", "#2563EB"],
                text=pdf["revenue_share_pct"].apply(lambda v: f"{v}%"),
                title="Revenue by Product — Top 10",
            )
            fig.update_traces(textposition="outside")
            fig.update_coloraxes(showscale=False)
            save(fig, "product_revenue", "Revenue by Product",
                 "Top 10 products by total revenue with share %")

        # ── 2. Monthly Trend + MoM Growth ─────────────────────────────────────
        monthly_dict = analytics.get("time_series", {}).get("monthly")
        if monthly_dict:
            mdf = pd.DataFrame(
                monthly_dict.items(), columns=["month", "revenue"]
            ).sort_values("month")
            mom = analytics.get("time_series", {}).get("mom_growth_pct", {})
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(
                x=mdf["month"], y=mdf["revenue"],
                mode="lines+markers", name="Revenue",
                line=dict(color="#2563EB", width=2.5),
                marker=dict(size=7),
            ), secondary_y=False)
            if mom:
                mom_df = pd.DataFrame(
                    mom.items(), columns=["month", "growth"]
                ).sort_values("month")
                bar_colors = [
                    "#059669" if v >= 0 else "#DC2626" for v in mom_df["growth"]
                ]
                fig.add_trace(go.Bar(
                    x=mom_df["month"], y=mom_df["growth"],
                    name="MoM Growth %",
                    marker_color=bar_colors, opacity=0.35,
                ), secondary_y=True)
            fig.update_layout(title="Monthly Revenue Trend + MoM Growth")
            fig.update_yaxes(
                title_text="Revenue ($)", secondary_y=False, gridcolor=GRID
            )
            fig.update_yaxes(title_text="MoM Growth (%)", secondary_y=True)
            save(fig, "monthly_trend", "Monthly Revenue Trend",
                 "Revenue over time with MoM growth overlay")

        # ── 3. Region Performance Bar ─────────────────────────────────────────
        region_data = analytics.get("region", {}).get("breakdown")
        if region_data and region_col:
            rdf = pd.DataFrame(region_data).sort_values(
                "total_revenue", ascending=False
            )
            fig = px.bar(
                rdf, x=region_col, y="total_revenue",
                color="total_revenue",
                color_continuous_scale=["#D1FAE5", "#059669"],
                text=rdf["revenue_share_pct"].apply(lambda v: f"{v}%"),
                title="Revenue by Region",
            )
            fig.update_traces(textposition="outside")
            fig.update_coloraxes(showscale=False)
            fig.update_yaxes(gridcolor=GRID)
            save(fig, "region_revenue", "Revenue by Region",
                 "Regional revenue performance with share %")

        # ── 4. Quarterly Bar ──────────────────────────────────────────────────
        quarterly_dict = analytics.get("time_series", {}).get("quarterly")
        if quarterly_dict and len(quarterly_dict) >= 2:
            qdf = pd.DataFrame(
                quarterly_dict.items(), columns=["quarter", "revenue"]
            ).sort_values("quarter")
            fig = px.bar(
                qdf, x="quarter", y="revenue",
                color_discrete_sequence=["#7C3AED"],
                title="Quarterly Revenue",
                text=qdf["revenue"].apply(lambda v: f"${v:,.0f}"),
            )
            fig.update_traces(textposition="outside")
            fig.update_yaxes(gridcolor=GRID)
            save(fig, "quarterly", "Quarterly Revenue",
                 "Revenue aggregated by quarter")

        # ── 5. Revenue Share Donut ────────────────────────────────────────────
        if prod_data and product_col:
            pdf  = pd.DataFrame(prod_data)
            top8 = pdf.head(8)
            fig  = go.Figure(go.Pie(
                labels=top8[product_col], values=top8["total_revenue"],
                hole=0.45, marker_colors=PALETTE[:len(top8)],
                textinfo="label+percent",
            ))
            fig.update_layout(title="Revenue Share by Product (Top 8)")
            save(fig, "revenue_share_donut", "Revenue Share Donut",
                 "Revenue share by product (top 8)")

        # ── 6. Top Customer Bar ───────────────────────────────────────────────
        cust_data = analytics.get("customer", {}).get("top_10")
        if cust_data and customer_col:
            cdf = pd.DataFrame(cust_data).sort_values("total_revenue")
            fig = px.bar(
                cdf, y=customer_col, x="total_revenue", orientation="h",
                color="total_revenue",
                color_continuous_scale=["#FEF3C7", "#D97706"],
                title="Top 10 Customers by Revenue",
                text=cdf["revenue_share_pct"].apply(lambda v: f"{v}%"),
            )
            fig.update_traces(textposition="outside")
            fig.update_coloraxes(showscale=False)
            save(fig, "top_customers", "Top 10 Customers",
                 "Highest revenue-generating customers")

        # ── 7. Correlation Heatmap ────────────────────────────────────────────
        corr = analytics.get("correlation_matrix")
        if corr and len(corr) >= 2:
            corr_df = pd.DataFrame(corr)
            fig = go.Figure(go.Heatmap(
                z=corr_df.values,
                x=list(corr_df.columns),
                y=list(corr_df.index),
                colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
                text=corr_df.round(2).values,
                texttemplate="%{text}",
            ))
            fig.update_layout(title="Numeric Column Correlation Heatmap")
            save(fig, "correlation_heatmap", "Correlation Heatmap",
                 "Pairwise correlations between numeric columns")

        # ── 8. KPI Summary Card ───────────────────────────────────────────────
        summary = analytics.get("summary", {})
        rev     = analytics.get("revenue", {})
        kpis = [
            ("Total Revenue",   f"${rev.get('total', 0):,.0f}"   if rev.get("total")   else "N/A"),
            ("Avg Transaction", f"${rev.get('average', 0):,.0f}" if rev.get("average") else "N/A"),
            ("Top Product",     str(summary.get("top_product", "N/A"))),
            ("Best Region",     str(summary.get("best_region",  "N/A"))),
            ("MoM Growth",
             f"{summary.get('latest_mom_growth_pct', 0):.1f}%"
             if summary.get("latest_mom_growth_pct") is not None else "N/A"),
            ("Best Month",      str(summary.get("best_month", "N/A"))),
        ]
        fig = go.Figure()
        cols_per_row = 3
        for i, (label, value) in enumerate(kpis):
            r, c = divmod(i, cols_per_row)
            fig.add_annotation(
                x=(c + 0.5) / cols_per_row,
                y=1 - (r * 0.5) - 0.1,
                text=(
                    f"<b style='font-size:22px'>{value}</b><br>"
                    f"<span style='font-size:13px;color:#6B7280'>{label}</span>"
                ),
                showarrow=False, xref="paper", yref="paper", align="center",
            )
        fig.update_layout(
            title="KPI Dashboard", height=300,
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(visible=False), yaxis=dict(visible=False),
        )
        kpi_path = f"{CHARTS_DIR}/{base}_kpi_dashboard.png"
        try:
            fig.write_image(kpi_path, width=1200, height=300, scale=1.5)
            chart_paths.append(kpi_path)
            chart_meta.append({
                "path": kpi_path,
                "title": "KPI Dashboard",
                "description": "Key performance indicators at a glance",
                "format": "png",
            })
            print("  [OK] KPI Dashboard")
        except Exception as kpi_err:
            print(f"  [WARN] KPI PNG failed: {kpi_err} — saving HTML")
            kpi_html = f"{CHARTS_DIR}/{base}_kpi_dashboard.html"
            fig.write_html(kpi_html)
            chart_paths.append(kpi_html)
            chart_meta.append({
                "path": kpi_html,
                "title": "KPI Dashboard",
                "description": "Key performance indicators at a glance",
                "format": "html",
            })

        # ── 9. Revenue vs Quantity Scatter ────────────────────────────────────
        if revenue_col and qty_col and product_col:
            sdf = df.groupby(product_col)[[revenue_col, qty_col]].sum().reset_index()
            fig = px.scatter(
                sdf, x=qty_col, y=revenue_col,
                size=revenue_col, color=product_col,
                hover_name=product_col,
                color_discrete_sequence=PALETTE,
                title="Revenue vs Quantity Sold (by Product)",
            )
            fig.update_yaxes(gridcolor=GRID)
            save(fig, "revenue_vs_qty", "Revenue vs Quantity",
                 "Bubble chart — size = revenue, position = qty vs revenue")

        # ── 10. Anomaly Chart ─────────────────────────────────────────────────
        anomalies = analytics.get("time_series", {}).get("anomaly_months", {})
        if monthly_dict and anomalies:
            mdf = pd.DataFrame(
                monthly_dict.items(), columns=["month", "revenue"]
            ).sort_values("month")
            adf = pd.DataFrame(
                anomalies.items(), columns=["month", "revenue"]
            )
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=mdf["month"], y=mdf["revenue"],
                mode="lines+markers", name="Revenue",
                line=dict(color="#2563EB", width=2),
            ))
            fig.add_trace(go.Scatter(
                x=adf["month"], y=adf["revenue"],
                mode="markers", name="Anomaly",
                marker=dict(color="#DC2626", size=14, symbol="x"),
            ))
            fig.update_layout(title="Monthly Revenue with Anomaly Detection")
            fig.update_yaxes(gridcolor=GRID)
            save(fig, "anomaly_chart", "Anomaly Detection",
                 "Months with revenue > 2 std deviations flagged")

        state["chart_paths"]    = chart_paths
        state["chart_metadata"] = chart_meta
        state["processing_time"]["visualizer"] = round(time.time() - t0, 2)
        print(f"  Total: {len(chart_paths)} charts in {state['processing_time']['visualizer']}s")

    except Exception as e:
        import traceback
        err = f"Visualizer: {e}"
        print(f"  [FAIL] {err}\n{traceback.format_exc()}")
        state["errors"].append(err)
        state["chart_paths"]    = []
        state["chart_metadata"] = []
        state["processing_time"]["visualizer"] = round(time.time() - t0, 2)

    return state


def _first(col_map: dict, role: str):
    cols = col_map.get(role, [])
    return cols[0] if cols else None