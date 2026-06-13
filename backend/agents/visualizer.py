"""
Agent 3 — Production Visualization Agent
Render-compatible: uses ONLY matplotlib (no kaleido, no Chrome needed)
All 10 charts saved as PNG — works on any server
"""

import os, time
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from core.state import AgentState

CHARTS_DIR = "static/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

COLORS = ["#2563EB","#7C3AED","#059669","#D97706","#DC2626",
          "#0891B2","#65A30D","#DB2777","#EA580C","#4F46E5"]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#f8fafc",
    "axes.edgecolor":   "#e2e8f0",
    "axes.grid":        True,
    "grid.color":       "#f1f5f9",
    "grid.linewidth":   0.8,
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   14,
    "axes.titleweight": "bold",
    "axes.titlecolor":  "#1e293b",
    "axes.labelcolor":  "#64748b",
    "xtick.color":      "#64748b",
    "ytick.color":      "#64748b",
    "axes.spines.top":  False,
    "axes.spines.right":False,
})


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
        customer_col = _first(col_map, "customer")

        def save(name, title, description):
            path = f"{CHARTS_DIR}/{base}_{name}.png"
            plt.savefig(path, dpi=150, bbox_inches="tight",
                        facecolor="white", edgecolor="none")
            plt.close("all")
            chart_paths.append(path)
            chart_meta.append({"path": path, "title": title,
                               "description": description, "format": "png"})
            print(f"  [OK] {title}")
            return path

        def fmt_money(x, _=None):
            if x >= 1_000_000: return f"${x/1_000_000:.1f}M"
            if x >= 1_000:     return f"${x/1_000:.0f}K"
            return f"${x:.0f}"

        # ── 1. Product Revenue Bar ────────────────────────────────────────────
        prod_data = analytics.get("product", {}).get("top_10")
        if prod_data and product_col and revenue_col:
            pdf = pd.DataFrame(prod_data).sort_values("total_revenue")
            fig, ax = plt.subplots(figsize=(12, max(5, len(pdf)*0.6)))
            bars = ax.barh(pdf[product_col], pdf["total_revenue"],
                           color=COLORS[0], alpha=0.85, height=0.6)
            for bar, pct in zip(bars, pdf["revenue_share_pct"]):
                ax.text(bar.get_width() + bar.get_width()*0.01,
                        bar.get_y() + bar.get_height()/2,
                        f"  {pct}%", va="center", fontsize=10, color="#374151")
            ax.xaxis.set_major_formatter(plt.FuncFormatter(fmt_money))
            ax.set_xlabel("Total Revenue")
            ax.set_title("Revenue by Product — Top 10")
            plt.tight_layout()
            save("product_revenue","Revenue by Product",
                 "Top 10 products by total revenue with share %")

        # ── 2. Monthly Trend + MoM Growth ─────────────────────────────────────
        monthly_dict = analytics.get("time_series", {}).get("monthly")
        if monthly_dict:
            mdf = pd.DataFrame(monthly_dict.items(),
                               columns=["month","revenue"]).sort_values("month")
            mom = analytics.get("time_series",{}).get("mom_growth_pct",{})
            fig, ax1 = plt.subplots(figsize=(13, 6))
            ax1.plot(range(len(mdf)), mdf["revenue"], "o-",
                     color=COLORS[0], linewidth=2.5, markersize=7, label="Revenue")
            ax1.fill_between(range(len(mdf)), mdf["revenue"],
                             alpha=0.08, color=COLORS[0])
            ax1.set_xticks(range(len(mdf)))
            ax1.set_xticklabels(mdf["month"], rotation=45, ha="right", fontsize=9)
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(fmt_money))
            ax1.set_ylabel("Revenue ($)")
            ax1.set_title("Monthly Revenue Trend + MoM Growth")
            if mom:
                ax2 = ax1.twinx()
                mom_df = pd.DataFrame(mom.items(),
                                      columns=["month","growth"]).sort_values("month")
                idxs = [list(mdf["month"]).index(m)
                        for m in mom_df["month"] if m in list(mdf["month"])]
                bar_colors = ["#059669" if v >= 0 else "#DC2626"
                              for v in mom_df["growth"]]
                ax2.bar(idxs, mom_df["growth"].values,
                        color=bar_colors, alpha=0.3, width=0.5, label="MoM %")
                ax2.set_ylabel("MoM Growth (%)", color="#64748b")
                ax2.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
            fig.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95))
            plt.tight_layout()
            save("monthly_trend","Monthly Revenue Trend",
                 "Revenue over time with MoM growth overlay")

        # ── 3. Region Bar ─────────────────────────────────────────────────────
        region_data = analytics.get("region",{}).get("breakdown")
        if region_data and region_col:
            rdf = pd.DataFrame(region_data).sort_values("total_revenue",ascending=False)
            fig, ax = plt.subplots(figsize=(10, 6))
            bar_colors = [COLORS[i % len(COLORS)] for i in range(len(rdf))]
            bars = ax.bar(rdf[region_col], rdf["total_revenue"],
                          color=bar_colors, alpha=0.85, width=0.6)
            for bar, pct in zip(bars, rdf["revenue_share_pct"]):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() * 1.02, f"{pct}%",
                        ha="center", fontsize=10, fontweight="bold")
            ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_money))
            ax.set_ylabel("Total Revenue")
            ax.set_title("Revenue by Region")
            plt.tight_layout()
            save("region_revenue","Revenue by Region",
                 "Regional revenue performance with share %")

        # ── 4. Quarterly Bar ──────────────────────────────────────────────────
        quarterly_dict = analytics.get("time_series",{}).get("quarterly")
        if quarterly_dict and len(quarterly_dict) >= 2:
            qdf = pd.DataFrame(quarterly_dict.items(),
                               columns=["quarter","revenue"]).sort_values("quarter")
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(qdf["quarter"], qdf["revenue"],
                          color=COLORS[1], alpha=0.85, width=0.5)
            for bar, val in zip(bars, qdf["revenue"]):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() * 1.02, fmt_money(val),
                        ha="center", fontsize=11, fontweight="bold")
            ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_money))
            ax.set_ylabel("Revenue")
            ax.set_title("Quarterly Revenue")
            plt.tight_layout()
            save("quarterly","Quarterly Revenue","Revenue aggregated by quarter")

        # ── 5. Revenue Share Donut ────────────────────────────────────────────
        if prod_data and product_col:
            top8 = pd.DataFrame(prod_data).head(8)
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(
                top8["total_revenue"],
                labels=top8[product_col],
                autopct="%1.1f%%",
                colors=COLORS[:len(top8)],
                pctdistance=0.78,
                wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
                startangle=90,
            )
            for at in autotexts:
                at.set_fontsize(9)
                at.set_color("white")
                at.set_fontweight("bold")
            ax.set_title("Revenue Share by Product (Top 8)", pad=20)
            plt.tight_layout()
            save("revenue_share_donut","Revenue Share Donut",
                 "Revenue share by product (top 8)")

        # ── 6. Top Customer Bar ───────────────────────────────────────────────
        cust_data = analytics.get("customer",{}).get("top_10")
        if cust_data and customer_col:
            cdf = pd.DataFrame(cust_data).sort_values("total_revenue")
            fig, ax = plt.subplots(figsize=(12, max(5, len(cdf)*0.6)))
            bars = ax.barh(cdf[customer_col], cdf["total_revenue"],
                           color=COLORS[3], alpha=0.85, height=0.6)
            for bar, pct in zip(bars, cdf["revenue_share_pct"]):
                ax.text(bar.get_width() + bar.get_width()*0.01,
                        bar.get_y() + bar.get_height()/2,
                        f"  {pct}%", va="center", fontsize=10)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(fmt_money))
            ax.set_xlabel("Total Revenue")
            ax.set_title("Top 10 Customers by Revenue")
            plt.tight_layout()
            save("top_customers","Top 10 Customers",
                 "Highest revenue-generating customers")

        # ── 7. Correlation Heatmap ────────────────────────────────────────────
        corr = analytics.get("correlation_matrix")
        if corr and len(corr) >= 2:
            corr_df = pd.DataFrame(corr)
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(corr_df.values, cmap="RdBu_r", vmin=-1, vmax=1,
                           aspect="auto")
            ax.set_xticks(range(len(corr_df.columns)))
            ax.set_yticks(range(len(corr_df.index)))
            ax.set_xticklabels(corr_df.columns, rotation=45, ha="right")
            ax.set_yticklabels(corr_df.index)
            for i in range(len(corr_df.index)):
                for j in range(len(corr_df.columns)):
                    v = corr_df.values[i, j]
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                            fontsize=10, color="white" if abs(v) > 0.5 else "#1e293b",
                            fontweight="bold")
            plt.colorbar(im, ax=ax, shrink=0.8)
            ax.set_title("Numeric Column Correlation Heatmap")
            plt.tight_layout()
            save("correlation_heatmap","Correlation Heatmap",
                 "Pairwise correlations between numeric columns")

        # ── 8. KPI Dashboard ─────────────────────────────────────────────────
        summary = analytics.get("summary", {})
        rev     = analytics.get("revenue", {})
        kpis = [
            ("Total Revenue",   fmt_money(rev.get("total",0)) if rev.get("total") else "N/A", COLORS[0]),
            ("Avg Transaction", fmt_money(rev.get("average",0)) if rev.get("average") else "N/A", COLORS[1]),
            ("Top Product",     str(summary.get("top_product","N/A")), COLORS[2]),
            ("Best Region",     str(summary.get("best_region","N/A")), COLORS[3]),
            ("MoM Growth",
             f"{summary.get('latest_mom_growth_pct',0):.1f}%"
             if summary.get("latest_mom_growth_pct") is not None else "N/A",
             COLORS[4] if (summary.get("latest_mom_growth_pct") or 0) >= 0 else COLORS[4]),
            ("Best Month",      str(summary.get("best_month","N/A")), COLORS[5]),
        ]
        fig = plt.figure(figsize=(14, 4), facecolor="white")
        fig.suptitle("KPI Dashboard", fontsize=16, fontweight="bold",
                     color="#1e293b", y=1.02)
        for i, (label, value, color) in enumerate(kpis):
            ax = fig.add_subplot(2, 3, i+1)
            ax.set_facecolor("#f8fafc")
            for spine in ax.spines.values():
                spine.set_edgecolor("#e2e8f0")
                spine.set_linewidth(1.5)
            ax.text(0.5, 0.62, value, transform=ax.transAxes,
                    fontsize=18, fontweight="bold", ha="center",
                    va="center", color=color)
            ax.text(0.5, 0.22, label, transform=ax.transAxes,
                    fontsize=9, ha="center", va="center",
                    color="#64748b", style="italic")
            ax.set_xticks([]); ax.set_yticks([])
        plt.tight_layout()
        save("kpi_dashboard","KPI Dashboard",
             "Key performance indicators at a glance")

        # ── 9. Revenue vs Quantity Scatter ────────────────────────────────────
        if revenue_col and qty_col and product_col:
            sdf = df.groupby(product_col)[[revenue_col, qty_col]].sum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 7))
            for i, (_, row) in enumerate(sdf.iterrows()):
                size = (row[revenue_col] / sdf[revenue_col].max()) * 2000 + 100
                ax.scatter(row[qty_col], row[revenue_col],
                           s=size, color=COLORS[i % len(COLORS)],
                           alpha=0.75, edgecolors="white", linewidth=1.5,
                           label=str(row[product_col]))
                ax.annotate(str(row[product_col]),
                            (row[qty_col], row[revenue_col]),
                            textcoords="offset points", xytext=(0, 10),
                            ha="center", fontsize=9, color="#374151")
            ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_money))
            ax.set_xlabel("Quantity Sold")
            ax.set_ylabel("Revenue ($)")
            ax.set_title("Revenue vs Quantity Sold (by Product)")
            ax.legend(loc="upper left", fontsize=9)
            plt.tight_layout()
            save("revenue_vs_qty","Revenue vs Quantity",
                 "Bubble chart — size = revenue, position = qty vs revenue")

        # ── 10. Anomaly Chart ─────────────────────────────────────────────────
        anomalies = analytics.get("time_series",{}).get("anomaly_months",{})
        if monthly_dict:
            mdf = pd.DataFrame(monthly_dict.items(),
                               columns=["month","revenue"]).sort_values("month")
            fig, ax = plt.subplots(figsize=(13, 6))
            ax.plot(range(len(mdf)), mdf["revenue"], "o-",
                    color=COLORS[0], linewidth=2.5, markersize=7, label="Revenue")
            ax.fill_between(range(len(mdf)), mdf["revenue"],
                            alpha=0.06, color=COLORS[0])
            if anomalies:
                for month, rev in anomalies.items():
                    if month in list(mdf["month"]):
                        idx = list(mdf["month"]).index(month)
                        ax.scatter(idx, rev, color=COLORS[4], s=200,
                                   marker="X", zorder=5, linewidth=2)
                        ax.annotate(f"Anomaly\n{fmt_money(rev)}",
                                    (idx, rev),
                                    textcoords="offset points",
                                    xytext=(0, 15), ha="center",
                                    fontsize=9, color=COLORS[4],
                                    fontweight="bold")
            ax.set_xticks(range(len(mdf)))
            ax.set_xticklabels(mdf["month"], rotation=45, ha="right", fontsize=9)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_money))
            ax.set_ylabel("Revenue ($)")
            ax.set_title("Monthly Revenue with Anomaly Detection")
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0],[0], color=COLORS[0], linewidth=2, label="Revenue"),
                Line2D([0],[0], marker="X", color=COLORS[4], linewidth=0,
                       markersize=10, label="Anomaly"),
            ]
            ax.legend(handles=legend_elements)
            plt.tight_layout()
            save("anomaly_chart","Anomaly Detection",
                 "Months with revenue > 2 std deviations flagged")

        state["chart_paths"]    = chart_paths
        state["chart_metadata"] = chart_meta
        state["processing_time"]["visualizer"] = round(time.time() - t0, 2)
        print(f"  Total: {len(chart_paths)} charts in "
              f"{state['processing_time']['visualizer']}s")

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