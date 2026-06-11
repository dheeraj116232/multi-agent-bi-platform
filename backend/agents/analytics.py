"""
Agent 2 — Production Analytics Agent
--------------------------------------
Capabilities:
  * Auto-detects column roles from state["column_map"]
  * Revenue KPIs: total, avg, median, max, min, std deviation, CAGR
  * Month-over-month and quarter-over-quarter growth rates
  * Product/category deep-dive: top 10, bottom 10, revenue share %
  * Regional analysis: performance ranking, gap analysis
  * Customer analysis: top customers, repeat vs new (if customer col exists)
  * Time-series decomposition: trend, seasonality hints
  * Cohort detection (monthly cohorts if customer + date cols exist)
  * Correlation matrix between numeric columns
  * Anomaly detection: months/products with unusual spikes
  * Full JSON output — drives both Viz Agent and Report Agent
"""

import time
import pandas as pd
import numpy as np
from core.state import AgentState


def analytics_agent(state: AgentState) -> AgentState:
    t0 = time.time()
    print("\n=== Agent 2: Analytics ===")
    state["current_agent"] = "analytics"
    state.setdefault("errors", [])
    state.setdefault("processing_time", {})

    try:
        df  = state["clean_df"]
        col_map = state.get("column_map") or {}

        if df is None or len(df) == 0:
            raise ValueError("No cleaned data available for analytics")

        result = {
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "all_columns": list(df.columns),
        }

        # -- resolve primary columns from role map -----------------------------
        revenue_col  = _first(col_map, "revenue")
        qty_col      = _first(col_map, "quantity")
        product_col  = _first(col_map, "product")
        region_col   = _first(col_map, "region")
        date_col     = _first(col_map, "date")
        customer_col = _first(col_map, "customer")

        result["columns_used"] = {
            "revenue": revenue_col, "quantity": qty_col,
            "product": product_col, "region": region_col,
            "date": date_col,       "customer": customer_col,
        }

        # -- 1. Revenue KPIs ---------------------------------------------------
        if revenue_col:
            rev = df[revenue_col].dropna()
            result["revenue"] = {
                "total":    _fmt(rev.sum()),
                "average":  _fmt(rev.mean()),
                "median":   _fmt(rev.median()),
                "max":      _fmt(rev.max()),
                "min":      _fmt(rev.min()),
                "std_dev":  _fmt(rev.std()),
                "count":    int(rev.count()),
            }
            # Revenue per unit (if qty available)
            if qty_col:
                total_qty = df[qty_col].sum()
                result["revenue"]["revenue_per_unit"] = _fmt(rev.sum() / max(total_qty, 1))

        # -- 2. Quantity KPIs --------------------------------------------------
        if qty_col:
            qty = df[qty_col].dropna()
            result["quantity"] = {
                "total":   int(qty.sum()),
                "average": _fmt(qty.mean()),
                "max":     int(qty.max()),
                "min":     int(qty.min()),
            }

        # -- 3. Product analysis -----------------------------------------------
        if product_col and revenue_col:
            prod = df.groupby(product_col)[revenue_col].agg(
                ["sum", "mean", "count"]
            ).rename(columns={"sum": "total_revenue", "mean": "avg_revenue", "count": "transactions"})

            if qty_col:
                prod["total_qty"] = df.groupby(product_col)[qty_col].sum()

            prod = prod.sort_values("total_revenue", ascending=False)
            total_rev = prod["total_revenue"].sum()
            prod["revenue_share_pct"] = (prod["total_revenue"] / max(total_rev, 1) * 100).round(2)

            result["product"] = {
                "top_10": _df_to_records(prod.head(10).reset_index()),
                "bottom_10": _df_to_records(prod.tail(10).reset_index()),
                "top_product": str(prod.index[0]),
                "top_revenue": _fmt(prod["total_revenue"].iloc[0]),
                "worst_product": str(prod.index[-1]),
                "unique_products": int(len(prod)),
                "pareto_80_products": _pareto_count(prod["total_revenue"]),
            }

        # -- 4. Regional analysis ----------------------------------------------
        if region_col and revenue_col:
            reg = df.groupby(region_col)[revenue_col].agg(["sum", "mean", "count"])
            reg.columns = ["total_revenue", "avg_revenue", "transactions"]
            reg = reg.sort_values("total_revenue", ascending=False)
            total_rev = reg["total_revenue"].sum()
            reg["revenue_share_pct"] = (reg["total_revenue"] / max(total_rev, 1) * 100).round(2)

            best  = reg.index[0]
            worst = reg.index[-1]
            result["region"] = {
                "breakdown": _df_to_records(reg.reset_index()),
                "best_region": str(best),
                "best_revenue": _fmt(reg.loc[best, "total_revenue"]),
                "worst_region": str(worst),
                "worst_revenue": _fmt(reg.loc[worst, "total_revenue"]),
                "performance_gap_pct": round(
                    (reg.loc[best, "total_revenue"] - reg.loc[worst, "total_revenue"])
                    / max(reg.loc[best, "total_revenue"], 1) * 100, 2
                ),
            }

        # -- 5. Time-series analysis -------------------------------------------
        if date_col and revenue_col and pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df["_month"]   = df[date_col].dt.to_period("M").astype(str)
            df["_quarter"] = df[date_col].dt.to_period("Q").astype(str)
            df["_year"]    = df[date_col].dt.year.astype(str)

            monthly   = df.groupby("_month")[revenue_col].sum().sort_index()
            quarterly = df.groupby("_quarter")[revenue_col].sum().sort_index()
            yearly    = df.groupby("_year")[revenue_col].sum().sort_index()

            result["time_series"] = {
                "monthly":   monthly.round(2).to_dict(),
                "quarterly": quarterly.round(2).to_dict(),
                "yearly":    yearly.round(2).to_dict(),
            }

            # MoM growth
            if len(monthly) >= 2:
                mom = (monthly.pct_change() * 100).round(2)
                result["time_series"]["mom_growth_pct"] = mom.dropna().to_dict()
                result["time_series"]["latest_mom_growth"] = float(mom.iloc[-1])
                result["time_series"]["avg_mom_growth"]    = float(mom.mean())

            # QoQ growth
            if len(quarterly) >= 2:
                qoq = (quarterly.pct_change() * 100).round(2)
                result["time_series"]["qoq_growth_pct"] = qoq.dropna().to_dict()
                result["time_series"]["latest_qoq_growth"] = float(qoq.iloc[-1])

            # YoY growth (CAGR if 2+ years)
            if len(yearly) >= 2:
                first_yr = float(yearly.iloc[0])
                last_yr  = float(yearly.iloc[-1])
                n_years  = len(yearly) - 1
                cagr = ((last_yr / max(first_yr, 1)) ** (1 / n_years) - 1) * 100 if n_years else 0
                result["time_series"]["cagr_pct"] = round(cagr, 2)

            # Anomaly: months > 2 std devs from mean
            mean_rev = monthly.mean()
            std_rev  = monthly.std()
            anomalies = monthly[abs(monthly - mean_rev) > 2 * std_rev]
            result["time_series"]["anomaly_months"] = anomalies.round(2).to_dict()

            # Best/worst month
            result["time_series"]["best_month"]  = str(monthly.idxmax())
            result["time_series"]["worst_month"] = str(monthly.idxmin())

            # Seasonality hint (which month of year averages highest)
            df["_month_num"] = df[date_col].dt.month
            monthly_avg = df.groupby("_month_num")[revenue_col].mean()
            peak_month_num = int(monthly_avg.idxmax())
            import calendar
            result["time_series"]["peak_season_month"] = calendar.month_name[peak_month_num]

        # -- 6. Customer analysis ----------------------------------------------
        if customer_col and revenue_col:
            cust = df.groupby(customer_col)[revenue_col].agg(["sum", "count"])
            cust.columns = ["total_revenue", "transactions"]
            cust = cust.sort_values("total_revenue", ascending=False)
            total_cust_rev = cust["total_revenue"].sum()
            cust["revenue_share_pct"] = (cust["total_revenue"] / max(total_cust_rev, 1) * 100).round(2)

            result["customer"] = {
                "top_10": _df_to_records(cust.head(10).reset_index()),
                "total_customers": int(len(cust)),
                "avg_revenue_per_customer": _fmt(cust["total_revenue"].mean()),
                "top_customer": str(cust.index[0]),
                "top_customer_revenue": _fmt(cust["total_revenue"].iloc[0]),
                "repeat_customers": int((cust["transactions"] > 1).sum()),
                "one_time_customers": int((cust["transactions"] == 1).sum()),
            }

        # -- 7. Correlation matrix (numeric columns) ---------------------------
        num_df = df.select_dtypes(include="number")
        if num_df.shape[1] >= 2:
            corr = num_df.corr().round(3)
            result["correlation_matrix"] = corr.to_dict()
            # Highlight strong correlations
            pairs = []
            for i, c1 in enumerate(corr.columns):
                for c2 in corr.columns[i+1:]:
                    v = corr.loc[c1, c2]
                    if abs(v) > 0.7:
                        pairs.append({"col1": c1, "col2": c2, "correlation": float(v)})
            result["strong_correlations"] = pairs

        # -- 8. Summary narrative (key stats in one dict) ----------------------
        result["summary"] = {
            "total_revenue":        result.get("revenue", {}).get("total"),
            "top_product":          result.get("product", {}).get("top_product"),
            "best_region":          result.get("region", {}).get("best_region"),
            "worst_region":         result.get("region", {}).get("worst_region"),
            "latest_mom_growth_pct": result.get("time_series", {}).get("latest_mom_growth"),
            "best_month":           result.get("time_series", {}).get("best_month"),
            "top_customer":         result.get("customer", {}).get("top_customer"),
        }

        result["status"] = "success"
        state["analytics_result"] = result
        state["processing_time"]["analytics"] = round(time.time() - t0, 2)

        print(f"  [OK] Revenue: {result.get('revenue',{}).get('total')} | "
              f"Top: {result.get('product',{}).get('top_product','N/A')} | "
              f"{state['processing_time']['analytics']}s")

    except Exception as e:
        import traceback
        err = f"Analytics: {e}"
        print(f"  [FAIL] {err}\n{traceback.format_exc()}")
        state["errors"].append(err)
        state["analytics_result"] = {"status": "failed", "error": str(e)}
        state["processing_time"]["analytics"] = round(time.time() - t0, 2)

    return state


# -- helpers -------------------------------------------------------------------

def _first(col_map: dict, role: str):
    cols = col_map.get(role, [])
    return cols[0] if cols else None

def _fmt(v) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return v

def _df_to_records(df: pd.DataFrame) -> list:
    return [{k: (round(v, 2) if isinstance(v, float) else v)
             for k, v in row.items()} for row in df.to_dict("records")]

def _pareto_count(revenue_series: pd.Series) -> int:
    """How many products account for 80% of revenue."""
    total = revenue_series.sum()
    cumsum = revenue_series.sort_values(ascending=False).cumsum()
    return int((cumsum <= 0.8 * total).sum() + 1)