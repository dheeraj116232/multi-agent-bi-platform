"""
Shared LangGraph state object.
Every agent reads from and writes to this TypedDict.
"""

from typing import TypedDict, Optional, Any


class AgentState(TypedDict):
    # ── Input ─────────────────────────────────────────────────────────────────
    raw_file_path: str
    filename: str

    # ── File loader output ────────────────────────────────────────────────────
    file_meta: Optional[dict]          # extension, size, sheets, encoding, etc.

    # ── Agent 1: Data Cleaning ────────────────────────────────────────────────
    clean_df: Optional[Any]            # pandas DataFrame
    cleaning_report: Optional[dict]

    # ── Agent 2: Analytics ───────────────────────────────────────────────────
    analytics_result: Optional[dict]
    column_map: Optional[dict]         # detected column roles

    # ── Agent 3: Visualization ───────────────────────────────────────────────
    chart_paths: Optional[list]
    chart_metadata: Optional[list]     # title + description per chart

    # ── Agent 4: Forecasting ─────────────────────────────────────────────────
    forecast_result: Optional[dict]

    # ── Agent 5: Executive Report ─────────────────────────────────────────────
    report_text: Optional[str]
    pdf_path: Optional[str]

    # ── Pipeline metadata ─────────────────────────────────────────────────────
    errors: Optional[list]
    warnings: Optional[list]
    current_agent: Optional[str]
    processing_time: Optional[dict]    # agent_name → seconds