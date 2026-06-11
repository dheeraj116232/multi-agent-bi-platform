"""
Production-grade file loader.
Supports: CSV, TSV, Excel (xlsx/xls/xlsm/ods), JSON, JSONL,
          Parquet, XML, Google Sheets export, ZIP containing data files.
"""

import os
import json
import zipfile
import tempfile
import chardet
import pandas as pd
from pathlib import Path
from typing import Optional


SUPPORTED_EXTENSIONS = {
    # Delimited
    ".csv", ".tsv", ".txt",
    # Excel family
    ".xlsx", ".xls", ".xlsm", ".xlsb", ".ods",
    # Semi-structured
    ".json", ".jsonl",
    # Binary columnar
    ".parquet", ".feather",
    # Markup
    ".xml",
    # Archives containing data
    ".zip",
}


def detect_encoding(path: str) -> str:
    """Detect file encoding using chardet."""
    with open(path, "rb") as f:
        raw = f.read(100_000)
    result = chardet.detect(raw)
    return result.get("encoding") or "utf-8"


def load_file(path: str) -> tuple[pd.DataFrame, dict]:
    """
    Load any supported file into a DataFrame.
    Returns (dataframe, metadata_dict).
    Raises ValueError for unsupported types.
    """
    path = str(path)
    ext = Path(path).suffix.lower()
    meta = {
        "original_path": path,
        "extension": ext,
        "file_size_kb": round(os.path.getsize(path) / 1024, 2),
    }

    # ── ZIP: find first data file inside ──────────────────────────────────────
    if ext == ".zip":
        return _load_zip(path, meta)

    # ── CSV / TSV / plain text ─────────────────────────────────────────────────
    if ext in (".csv", ".tsv", ".txt"):
        return _load_delimited(path, ext, meta)

    # ── Excel family ──────────────────────────────────────────────────────────
    if ext in (".xlsx", ".xlsm"):
        return _load_excel(path, engine="openpyxl", meta=meta)
    if ext == ".xls":
        return _load_excel(path, engine="xlrd", meta=meta)
    if ext == ".xlsb":
        return _load_excel(path, engine="pyxlsb", meta=meta)
    if ext == ".ods":
        return _load_excel(path, engine="odf", meta=meta)

    # ── JSON / JSONL ───────────────────────────────────────────────────────────
    if ext in (".json", ".jsonl"):
        return _load_json(path, ext, meta)

    # ── Parquet / Feather ──────────────────────────────────────────────────────
    if ext == ".parquet":
        df = pd.read_parquet(path)
        meta["loader"] = "pandas.read_parquet"
        meta["rows"], meta["cols"] = df.shape
        return df, meta
    if ext == ".feather":
        df = pd.read_feather(path)
        meta["loader"] = "pandas.read_feather"
        meta["rows"], meta["cols"] = df.shape
        return df, meta

    # ── XML ────────────────────────────────────────────────────────────────────
    if ext == ".xml":
        return _load_xml(path, meta)

    raise ValueError(
        f"Unsupported file type: '{ext}'. "
        f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Private loaders
# ──────────────────────────────────────────────────────────────────────────────

def _load_delimited(path: str, ext: str, meta: dict) -> tuple[pd.DataFrame, dict]:
    sep = "\t" if ext == ".tsv" else ","
    encoding = detect_encoding(path)

    # Auto-detect separator if .txt
    if ext == ".txt":
        with open(path, "r", encoding=encoding, errors="replace") as f:
            sample = f.read(4096)
        tab_count = sample.count("\t")
        comma_count = sample.count(",")
        pipe_count = sample.count("|")
        sep = "\t" if tab_count > comma_count else ("|" if pipe_count > comma_count else ",")

    try:
        df = pd.read_csv(
            path,
            sep=sep,
            encoding=encoding,
            on_bad_lines="skip",
            low_memory=False,
        )
    except Exception:
        # Fallback: try utf-8 with error replacement
        df = pd.read_csv(path, sep=sep, encoding="utf-8", errors="replace",
                         on_bad_lines="skip", low_memory=False)

    meta.update({"loader": "pandas.read_csv", "encoding": encoding,
                 "separator": repr(sep), "rows": len(df), "cols": len(df.columns)})
    return df, meta


def _load_excel(path: str, engine: str, meta: dict) -> tuple[pd.DataFrame, dict]:
    xl = pd.ExcelFile(path, engine=engine)
    sheet_names = xl.sheet_names
    meta["sheets"] = sheet_names

    if len(sheet_names) == 1:
        df = xl.parse(sheet_names[0])
        meta["sheet_loaded"] = sheet_names[0]
    else:
        # Pick the sheet with the most data
        best_sheet, best_size = sheet_names[0], 0
        for s in sheet_names:
            tmp = xl.parse(s)
            if tmp.size > best_size:
                best_sheet, best_size = s, tmp.size
        df = xl.parse(best_sheet)
        meta["sheet_loaded"] = best_sheet
        meta["other_sheets"] = [s for s in sheet_names if s != best_sheet]

    meta.update({"loader": f"pandas.read_excel({engine})",
                 "rows": len(df), "cols": len(df.columns)})
    return df, meta


def _load_json(path: str, ext: str, meta: dict) -> tuple[pd.DataFrame, dict]:
    encoding = detect_encoding(path)
    if ext == ".jsonl":
        records = []
        with open(path, "r", encoding=encoding, errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        df = pd.json_normalize(records)
        meta["loader"] = "jsonl"
    else:
        with open(path, "r", encoding=encoding, errors="replace") as f:
            raw = json.load(f)
        # Handle dict-of-records, list-of-records, or nested
        if isinstance(raw, list):
            df = pd.json_normalize(raw)
        elif isinstance(raw, dict):
            # Try common keys: "data", "records", "rows", "results"
            for key in ("data", "records", "rows", "results", "items"):
                if key in raw and isinstance(raw[key], list):
                    df = pd.json_normalize(raw[key])
                    meta["json_key_used"] = key
                    break
            else:
                df = pd.json_normalize([raw])
        else:
            raise ValueError("JSON root must be an array or object")
        meta["loader"] = "json_normalize"

    meta.update({"rows": len(df), "cols": len(df.columns)})
    return df, meta


def _load_xml(path: str, meta: dict) -> tuple[pd.DataFrame, dict]:
    try:
        df = pd.read_xml(path)
        meta["loader"] = "pandas.read_xml"
    except Exception:
        # Fallback: flatten with lxml
        try:
            import lxml.etree as ET
            tree = ET.parse(path)
            root = tree.getroot()
            records = []
            for child in root:
                record = {}
                for elem in child:
                    record[elem.tag] = elem.text
                if record:
                    records.append(record)
            df = pd.DataFrame(records)
            meta["loader"] = "lxml_manual"
        except Exception as e:
            raise ValueError(f"XML parsing failed: {e}")

    meta.update({"rows": len(df), "cols": len(df.columns)})
    return df, meta


def _load_zip(path: str, meta: dict) -> tuple[pd.DataFrame, dict]:
    with zipfile.ZipFile(path, "r") as z:
        names = z.namelist()
        meta["zip_contents"] = names
        # Find first supported data file
        data_files = [
            n for n in names
            if Path(n).suffix.lower() in SUPPORTED_EXTENSIONS - {".zip"}
            and not n.startswith("__MACOSX")
        ]
        if not data_files:
            raise ValueError(f"No supported data files found inside ZIP. Contents: {names}")
        target = data_files[0]
        meta["zip_file_loaded"] = target
        with tempfile.NamedTemporaryFile(
            suffix=Path(target).suffix, delete=False
        ) as tmp:
            tmp.write(z.read(target))
            tmp_path = tmp.name
    try:
        df, inner_meta = load_file(tmp_path)
        meta.update(inner_meta)
        return df, meta
    finally:
        os.unlink(tmp_path)