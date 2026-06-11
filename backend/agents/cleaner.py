"""
Agent 1 — Production Data Cleaning Agent
-----------------------------------------
Capabilities:
  * Multi-format loading (CSV, TSV, Excel, JSON, JSONL, Parquet, XML, ZIP)
  * Smart encoding detection
  * Multi-sheet Excel (picks most data-rich sheet)
  * Column name standardisation
  * Duplicate removal (exact + near-duplicate hash detection)
  * Missing value strategy: numeric->median, categorical->mode, date->ffill
  * Currency/percentage string -> numeric ("$1,200.50" -> 1200.50)
  * Outlier removal IQR 2.0× (less aggressive for business data)
  * Automatic date parsing with 14 format attempts
  * Column role detection (revenue, qty, date, product, region, customer)
  * Data quality score (0–100)
"""

import time, re, hashlib
from typing import Optional

import pandas as pd
import numpy as np

from core.state import AgentState
from utils.file_loader import load_file

DATE_FORMATS = [
    "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y",
    "%Y/%m/%d", "%d.%m.%Y", "%Y%m%d",
    "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S",
    "%b %d, %Y", "%B %d, %Y", "%d %b %Y",
]

DATE_KW     = {"date","time","day","month","year","created","updated","timestamp","period"}
REVENUE_KW  = {"revenue","sales","amount","price","total","value","income",
               "cost","profit","gross","net","earning","billing","payment"}
QTY_KW      = {"quantity","qty","units","count","orders","volume","sold","number"}
PRODUCT_KW  = {"product","category","item","name","type","sku","brand","model","service"}
REGION_KW   = {"region","city","state","country","location","area","zone",
               "territory","market","branch","district","store"}
CUSTOMER_KW = {"customer","client","user","buyer","account","contact","member"}


def data_cleaning_agent(state: AgentState) -> AgentState:
    t0 = time.time()
    print("\n=== Agent 1: Data Cleaning ===")
    state["current_agent"] = "cleaner"
    state.setdefault("errors", [])
    state.setdefault("warnings", [])
    state.setdefault("processing_time", {})

    try:
        # 1. Load file (any supported format)
        df, file_meta = load_file(state["raw_file_path"])
        state["file_meta"] = file_meta
        print(f"  Loaded {file_meta['rows']}r x {file_meta['cols']}c  [{file_meta['extension']}  {file_meta['file_size_kb']} KB]")

        report = {
            "original_rows": len(df),
            "original_cols": len(df.columns),
            "original_columns": list(df.columns),
        }

        # 2. Drop entirely empty rows/columns
        df.dropna(how="all", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        report["empty_rows_dropped"] = report["original_rows"] - len(df)

        # 3. Standardise column names
        df.columns = (
            df.columns.astype(str).str.strip().str.lower()
            .str.replace(r"\s+", "_", regex=True)
            .str.replace(r"[^a-z0-9_]", "", regex=True)
            .str.replace(r"_+", "_", regex=True)
            .str.strip("_")
        )
        # de-duplicate column names
        cols = list(df.columns)
        seen = {}
        new_cols = []
        for c in cols:
            if c in seen:
                seen[c] += 1
                new_cols.append(f"{c}_{seen[c]}")
            else:
                seen[c] = 0
                new_cols.append(c)
        df.columns = new_cols
        report["standardised_columns"] = list(df.columns)

        # 4. Currency / percentage strings -> numeric
        currency_re = re.compile(r"^[\$\€\£\¥\₹]?\s*-?[\d,]+\.?\d*\s*[%]?$")
        converted_cols = []
        for col in df.select_dtypes(include="object").columns:
            sample = df[col].dropna().head(50).astype(str)
            if len(sample) and sample.str.match(currency_re).mean() > 0.7:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(r"[\$\€\£\¥\₹,\s]", "", regex=True)
                    .str.replace("%", "", regex=False)
                    .pipe(pd.to_numeric, errors="coerce")
                )
                converted_cols.append(col)
        report["currency_cols_converted"] = converted_cols

        # 5. Parse date columns
        date_cols_parsed = []
        for col in df.columns:
            cl = col.lower()
            if any(kw in cl for kw in DATE_KW):
                parsed = _try_parse_date(df[col])
                if parsed is not None:
                    df[col] = parsed
                    date_cols_parsed.append(col)
        report["date_cols_parsed"] = date_cols_parsed

        # 6. Infer remaining numeric columns from object dtype
        for col in df.select_dtypes(include="object").columns:
            conv = pd.to_numeric(df[col], errors="coerce")
            if conv.notna().mean() > 0.85:
                df[col] = conv

        # 7. Exact duplicate removal
        before = len(df)
        df.drop_duplicates(inplace=True)
        report["exact_duplicates_removed"] = before - len(df)

        # 8. Near-duplicate detection (hash on numeric fingerprint)
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if len(num_cols) >= 2:
            hashes = df[num_cols].round(2).astype(str).agg("|".join, axis=1).apply(
                lambda x: hashlib.md5(x.encode()).hexdigest()
            )
            near = int(hashes.duplicated().sum())
            if near:
                state["warnings"].append(
                    f"{near} near-duplicate rows (identical numeric fingerprint) — not auto-removed"
                )
            report["near_duplicates_flagged"] = near

        # 9. Fill missing values
        missing_before = int(df.isnull().sum().sum())
        missing_by_col = df.isnull().sum()

        for col in df.select_dtypes(include="number").columns:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())

        for col in df.select_dtypes(include="object").columns:
            if df[col].isna().any():
                mode = df[col].mode()
                df[col] = df[col].fillna(mode.iloc[0] if len(mode) else "unknown")

        for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
            df[col] = df[col].ffill().bfill()

        report["missing_values_before"] = missing_before
        report["missing_values_after"]  = int(df.isnull().sum().sum())

        high_null = missing_by_col[missing_by_col / max(len(df), 1) > 0.5].index.tolist()
        if high_null:
            state["warnings"].append(f"High null rate (>50%) in: {high_null}")

        # 10. Outlier removal (IQR 2.0x — gentler for business data)
        before = len(df)
        outlier_detail = {}
        for col in df.select_dtypes(include="number").columns:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lo, hi = q1 - 2.0 * iqr, q3 + 2.0 * iqr
            bad = (~df[col].between(lo, hi)).sum()
            if bad:
                outlier_detail[col] = int(bad)
                df = df[df[col].between(lo, hi)]
        report["outliers_removed_by_col"] = outlier_detail
        report["total_outliers_removed"] = before - len(df)

        # 11. Detect column business roles
        col_map = _detect_column_roles(df)
        state["column_map"] = col_map
        report["column_roles"] = col_map

        # 12. Data quality score
        # _quality_score expects final_rows to exist, so set it before scoring.
        report["final_rows"] = len(df)
        report["final_cols"] = len(df.columns)
        report["final_columns"] = list(df.columns)
        report["dtypes"] = {c: str(t) for c, t in df.dtypes.items()}
        report["status"] = "success"
        report["quality_score"] = _quality_score(df, report)

        # 13. Final summary
        # (final_* fields already set before quality scoring)

        state["clean_df"]       = df
        state["cleaning_report"] = report
        state["processing_time"]["cleaner"] = round(time.time() - t0, 2)

        print(f"  [OK] {report['original_rows']}->{report['final_rows']} rows | "
              f"quality={report['quality_score']}/100 | {state['processing_time']['cleaner']}s")

    except Exception as e:
        import traceback
        err = f"Cleaner: {e}"
        print(f"  [FAIL] {err}\n{traceback.format_exc()}")
        state["errors"].append(err)
        state["cleaning_report"] = {"status": "failed", "error": str(e)}
        state["processing_time"]["cleaner"] = round(time.time() - t0, 2)

    return state


# -- helpers -------------------------------------------------------------------

def _try_parse_date(series: pd.Series) -> Optional[pd.Series]:
    try:
        return pd.to_datetime(series, infer_datetime_format=True, errors="coerce")
    except Exception:
        pass
    for fmt in DATE_FORMATS:
        try:
            result = pd.to_datetime(series, format=fmt, errors="coerce")
            if result.notna().mean() > 0.5:
                return result
        except Exception:
            continue
    return None


def _detect_column_roles(df: pd.DataFrame) -> dict:
    roles: dict = {k: [] for k in ("revenue","quantity","date","product","region","customer","id","other")}
    for col in df.columns:
        cl  = col.lower()
        dt  = str(df[col].dtype)
        is_num = "float" in dt or "int" in dt
        is_dt  = "datetime" in dt

        if is_dt or any(kw in cl for kw in DATE_KW):
            roles["date"].append(col)
        elif any(kw in cl for kw in REVENUE_KW) and is_num:
            roles["revenue"].append(col)
        elif any(kw in cl for kw in QTY_KW) and is_num:
            roles["quantity"].append(col)
        elif any(kw in cl for kw in PRODUCT_KW):
            roles["product"].append(col)
        elif any(kw in cl for kw in REGION_KW):
            roles["region"].append(col)
        elif any(kw in cl for kw in CUSTOMER_KW):
            roles["customer"].append(col)
        elif cl.endswith("_id") or cl == "id":
            roles["id"].append(col)
        elif is_num and not roles["revenue"]:
            roles["revenue"].append(col)   # fallback: first unknown numeric = revenue
        else:
            roles["other"].append(col)

    return {k: v for k, v in roles.items() if v}


def _quality_score(df: pd.DataFrame, report: dict) -> int:
    score = 100
    null_rate = df.isnull().sum().sum() / max(df.shape[0] * df.shape[1], 1)
    score -= int(null_rate * 40)
    dup_rate = report.get("exact_duplicates_removed", 0) / max(report["original_rows"], 1)
    score -= int(dup_rate * 20)
    if report["final_rows"] < 10:  score -= 20
    elif report["final_rows"] < 50: score -= 10
    out_rate = report.get("total_outliers_removed", 0) / max(report["original_rows"], 1)
    score -= int(out_rate * 20)
    return max(0, min(100, score))
