"""
Agent 4 — Production Forecasting Agent
----------------------------------------
Models tried in order (best available wins):
  1. Prophet      — handles seasonality, holidays, missing dates
  2. XGBoost      — gradient boosting with lag features
  3. ARIMA        — classical time-series (statsmodels)
  4. Linear Regression — fallback (always available)

For each model:
  * 3-month and 6-month horizon forecasts
  * 80% and 95% confidence intervals (where available)
  * Model performance: MAE, RMSE, MAPE on last 20% of data
  * Trend direction: accelerating / decelerating / stable
  * Seasonality analysis
  * Revenue target scenarios: optimistic (+20%), realistic, pessimistic (-20%)
"""

import time, warnings
import pandas as pd
import numpy as np
from core.state import AgentState

warnings.filterwarnings("ignore")


def forecast_agent(state: AgentState) -> AgentState:
    t0 = time.time()
    print("\n=== Agent 4: Forecasting ===")
    state["current_agent"] = "forecaster"
    state.setdefault("errors", [])
    state.setdefault("processing_time", {})

    try:
        analytics = state["analytics_result"] or {}
        monthly   = analytics.get("time_series", {}).get("monthly", {})

        if len(monthly) < 3:
            state["forecast_result"] = {
                "status": "skipped",
                "reason": f"Need ≥3 months of data, got {len(monthly)}",
            }
            print(f"  ⚠ Skipped — insufficient data ({len(monthly)} months)")
            state["processing_time"]["forecaster"] = round(time.time() - t0, 2)
            return state

        # Build time-series DataFrame
        ts = (
            pd.DataFrame(monthly.items(), columns=["ds", "y"])
            .assign(ds=lambda d: pd.to_datetime(d["ds"]))
            .sort_values("ds")
            .reset_index(drop=True)
        )

        # Train / test split (80/20, min 1 test point)
        split = max(int(len(ts) * 0.8), len(ts) - 3)
        train, test = ts.iloc[:split], ts.iloc[split:]

        results = {}
        best_model = None
        best_mape  = float("inf")

        # -- 1. Prophet --------------------------------------------------------
        try:
            from prophet import Prophet
            m = Prophet(
                yearly_seasonality=(len(ts) >= 12),
                weekly_seasonality=False,
                daily_seasonality=False,
                seasonality_mode="multiplicative" if ts["y"].std() / ts["y"].mean() > 0.3 else "additive",
                interval_width=0.80,
                changepoint_prior_scale=0.05,
            )
            m.fit(train)
            future = m.make_future_dataframe(periods=6, freq="MS")
            fc     = m.predict(future)
            test_pred = fc.loc[fc["ds"].isin(test["ds"]), "yhat"].values
            metrics = _metrics(test["y"].values, test_pred[:len(test)])
            future_fc = fc[fc["ds"] > ts["ds"].max()].head(6)
            results["prophet"] = {
                "metrics": metrics,
                "forecast_3m": _fc_rows(future_fc, m, 3),
                "forecast_6m": _fc_rows(future_fc, m, 6),
                "has_ci": True,
            }
            if metrics["mape"] < best_mape:
                best_mape, best_model = metrics["mape"], "prophet"
            print(f"  Prophet MAPE={metrics['mape']:.1f}%")
        except Exception as e:
            print(f"  Prophet unavailable: {e}")

        # -- 2. XGBoost with lag features --------------------------------------
        try:
            from xgboost import XGBRegressor
            df_feat = _make_lag_features(ts)
            feat_cols = [c for c in df_feat.columns if c not in ["ds","y"]]
            X, y = df_feat[feat_cols].values, df_feat["y"].values
            sp = max(int(len(X) * 0.8), len(X) - 3)
            Xtr, Xte, ytr, yte = X[:sp], X[sp:], y[:sp], y[sp:]
            # Faster settings to keep pipeline responsive on small/medium inputs.
            xgb = XGBRegressor(n_estimators=80, learning_rate=0.05,
                               max_depth=4, random_state=42, verbosity=0)
            xgb.fit(Xtr, ytr)
            ypred = xgb.predict(Xte)
            metrics = _metrics(yte, ypred)
            # Forecast future 6 months by rolling prediction
            future_vals = _xgb_rolling_forecast(xgb, df_feat, feat_cols, n=6)
            future_months = pd.date_range(ts["ds"].max(), periods=7, freq="MS")[1:]
            fc_rows = [{"month": str(d.to_period("M")), "forecast": round(float(v), 2)}
                       for d, v in zip(future_months, future_vals)]
            results["xgboost"] = {
                "metrics": metrics,
                "forecast_3m": fc_rows[:3],
                "forecast_6m": fc_rows,
                "has_ci": False,
            }
            if metrics["mape"] < best_mape:
                best_mape, best_model = metrics["mape"], "xgboost"
            print(f"  XGBoost MAPE={metrics['mape']:.1f}%")
        except Exception as e:
            print(f"  XGBoost unavailable: {e}")

        # -- 3. ARIMA ----------------------------------------------------------
        try:
            from statsmodels.tsa.arima.model import ARIMA
            order = _auto_arima_order(train["y"])
            arima = ARIMA(train["y"].values, order=order).fit()
            test_pred = arima.forecast(steps=len(test))
            metrics = _metrics(test["y"].values, test_pred)
            fc_full = arima.forecast(steps=6)
            future_months = pd.date_range(ts["ds"].max(), periods=7, freq="MS")[1:]
            fc_rows = [{"month": str(d.to_period("M")), "forecast": round(float(v), 2)}
                       for d, v in zip(future_months, fc_full)]
            results["arima"] = {
                "metrics": metrics,
                "order": order,
                "forecast_3m": fc_rows[:3],
                "forecast_6m": fc_rows,
                "has_ci": False,
            }
            if metrics["mape"] < best_mape:
                best_mape, best_model = metrics["mape"], "arima"
            print(f"  ARIMA{order} MAPE={metrics['mape']:.1f}%")
        except Exception as e:
            print(f"  ARIMA unavailable: {e}")

        # -- 4. Linear Regression fallback (always runs) -----------------------
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures
        X_tr = np.arange(len(train)).reshape(-1,1)
        X_te = np.arange(len(train), len(ts)).reshape(-1,1)
        poly = PolynomialFeatures(degree=min(2, len(train)-1))
        Xp_tr = poly.fit_transform(X_tr)
        Xp_te = poly.transform(X_te)
        lr = LinearRegression().fit(Xp_tr, train["y"].values)
        te_pred = lr.predict(Xp_te) if len(X_te) else np.array([])
        metrics = _metrics(test["y"].values, te_pred) if len(te_pred) else {"mape": 999}
        X_fut = np.arange(len(ts), len(ts)+6).reshape(-1,1)
        fut_vals = lr.predict(poly.transform(X_fut))
        future_months = pd.date_range(ts["ds"].max(), periods=7, freq="MS")[1:]
        fc_rows = [{"month": str(d.to_period("M")), "forecast": max(0, round(float(v), 2))}
                   for d, v in zip(future_months, fut_vals)]
        results["linear_regression"] = {
            "metrics": metrics,
            "forecast_3m": fc_rows[:3],
            "forecast_6m": fc_rows,
            "has_ci": False,
        }
        if metrics["mape"] < best_mape:
            best_mape, best_model = metrics["mape"], "linear_regression"
        if not best_model:
            best_model = "linear_regression"
        print(f"  Linear MAPE={metrics.get('mape',999):.1f}%")

        # -- Compile best result -----------------------------------------------
        best = results[best_model]
        fc3  = best["forecast_3m"]
        fc6  = best["forecast_6m"]

        next_month_val = float(fc3[0]["forecast"]) if fc3 else 0
        q_total        = sum(r["forecast"] for r in fc3)
        h_total        = sum(r["forecast"] for r in fc6)
        last_actual    = float(ts["y"].iloc[-1])

        growth_pct = ((next_month_val - last_actual) / max(last_actual, 1)) * 100

        trend = _trend_direction(ts["y"].values)

        result = {
            "status":        "success",
            "best_model":    best_model,
            "best_mape_pct": round(best_mape, 2),
            "all_models":    {k: v["metrics"] for k, v in results.items()},
            "forecast_3m":   fc3,
            "forecast_6m":   fc6,
            "next_month":    round(next_month_val, 2),
            "next_quarter":  round(q_total, 2),
            "next_6_months": round(h_total, 2),
            "expected_growth_pct": round(growth_pct, 2),
            "trend_direction": trend,
            "scenarios": {
                "optimistic":  round(next_month_val * 1.20, 2),
                "realistic":   round(next_month_val, 2),
                "pessimistic": round(next_month_val * 0.80, 2),
            },
            "confidence": "high" if best_mape < 10 else "medium" if best_mape < 25 else "low",
        }

        state["forecast_result"] = result
        state["processing_time"]["forecaster"] = round(time.time() - t0, 2)
        print(f"  [OK] Best={best_model} MAPE={best_mape:.1f}% | "
              f"Next month=${next_month_val:,.0f} | {state['processing_time']['forecaster']}s")

    except Exception as e:
        import traceback
        err = f"Forecaster: {e}"
        print(f"  [FAIL] {err}\n{traceback.format_exc()}")
        state["errors"].append(err)
        state["forecast_result"] = {"status": "failed", "error": str(e)}
        state["processing_time"]["forecaster"] = round(time.time() - t0, 2)

    return state


# -- helpers -------------------------------------------------------------------

def _metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    if len(actual) == 0 or len(predicted) == 0:
        return {"mae": 0, "rmse": 0, "mape": 999}
    n   = min(len(actual), len(predicted))
    a, p = actual[:n], predicted[:n]
    mae  = float(np.mean(np.abs(a - p)))
    rmse = float(np.sqrt(np.mean((a - p)**2)))
    mape = float(np.mean(np.abs((a - p) / np.where(a == 0, 1, a))) * 100)
    return {"mae": round(mae, 2), "rmse": round(rmse, 2), "mape": round(mape, 2)}


def _fc_rows(future_df, model, n: int) -> list:
    rows = []
    for _, r in future_df.head(n).iterrows():
        row = {"month": str(r["ds"].to_period("M")), "forecast": round(float(r["yhat"]), 2)}
        if "yhat_lower" in r:
            row["lower_80"] = round(float(r["yhat_lower"]), 2)
            row["upper_80"] = round(float(r["yhat_upper"]), 2)
        rows.append(row)
    return rows


def _make_lag_features(ts: pd.DataFrame, lags=(1,2,3,6)) -> pd.DataFrame:
    df = ts.copy()
    df["month_num"]  = df["ds"].dt.month
    df["quarter"]    = df["ds"].dt.quarter
    df["trend"]      = np.arange(len(df))
    df["rolling_3m"] = df["y"].rolling(3, min_periods=1).mean()
    for lag in lags:
        df[f"lag_{lag}"] = df["y"].shift(lag)
    return df.dropna()


def _xgb_rolling_forecast(model, hist_df, feat_cols, n: int) -> list:
    df = hist_df.copy()
    preds = []
    for i in range(n):
        last_row = df.iloc[-1].copy()
        # Shift lags
        next_row = last_row.copy()
        next_row["trend"]  += 1
        next_row["month_num"] = ((last_row["month_num"]) % 12) + 1
        next_row["quarter"] = (next_row["month_num"] - 1) // 3 + 1
        for lag in (6, 3, 2, 1):
            col = f"lag_{lag}"
            if col in next_row.index:
                next_row[col] = df["y"].iloc[-lag] if lag <= len(df) else df["y"].mean()
        next_row["rolling_3m"] = df["y"].tail(3).mean()
        X = np.array([[next_row[c] for c in feat_cols if c in next_row.index]])
        pred = float(model.predict(X)[0])
        preds.append(max(0, pred))
        new_row = next_row.copy()
        new_row["y"] = pred
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
    return preds


def _auto_arima_order(series: pd.Series) -> tuple:
    """Simple order selection: test (1,1,1) vs (0,1,1) vs (1,1,0)."""
    from statsmodels.tsa.arima.model import ARIMA
    best_aic, best_order = float("inf"), (1,1,1)
    for order in [(1,1,1),(0,1,1),(1,1,0),(2,1,0),(0,1,2)]:
        try:
            aic = ARIMA(series.values, order=order).fit().aic
            if aic < best_aic:
                best_aic, best_order = aic, order
        except Exception:
            pass
    return best_order


def _trend_direction(values: np.ndarray) -> str:
    if len(values) < 3:
        return "insufficient data"
    first_half  = values[:len(values)//2].mean()
    second_half = values[len(values)//2:].mean()
    change_pct  = (second_half - first_half) / max(abs(first_half), 1) * 100
    if change_pct > 10:
        return "accelerating upward"
    elif change_pct > 2:
        return "growing steadily"
    elif change_pct < -10:
        return "declining"
    elif change_pct < -2:
        return "slowing"
    else:
        return "stable"