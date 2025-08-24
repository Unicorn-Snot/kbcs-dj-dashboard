# data_loader.py
# Load data from Google Sheets and normalize columns across years.

import streamlit as st
import pandas as pd
from urllib.parse import quote
from typing import Optional, Dict, List

# === Configure sheets by year ===
SHEETS: Dict[str, Dict[str, str]] = {
    "2022": {
        "sheet_id": "1wh65x9uwfQHDGax0xhR_Q2tZSdfyBlLMw3gMlTXIZl0",
        "gid": "1807168814",
        "program_column": "Section Name",
    },
    "2023": {
        "sheet_id": "17_GLEJvCUgUiFIAltzSIGDpXULFTCPih9kca5SGywd4",
        "gid": "581575423",
        "program_column": "Program Name",
    },
    "2024": {
        "sheet_id": "1_j2ElPU3AswjefXimiJQ3pIrG9loKNOVNi2SeXpb21o",
        "gid": "169834391",
        "program_column": "Program Name",
    },
}

def _csv_url(sheet_id: str, gid: Optional[str] = None, tab: Optional[str] = None) -> str:
    if gid:
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    if tab:
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={quote(tab)}"
    raise ValueError("Provide either gid or tab")

def _coerce_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0)

def _normalize_headers_and_columns(df: pd.DataFrame, expected_program_header: str) -> pd.DataFrame:
    """
    Normalize column names across years to a single schema the app expects.
    Keeps only the fields you actually use right now:
      program, items selected, percent of total, total items selected,
      on_demand items selected, channel, title, pn, _id
    """
    # 1) lower/strip all headers
    df = df.rename(columns=lambda c: str(c).strip().lower())

    # 2) base alias map (only map if present)
    alias_map = {
        "section name": "section",          # may be promoted to 'program' below
        "program name": "program",
        "title": "title",
        "channel": "channel",
        "items selected": "items selected",
        "total items selected": "total items selected",
        "percent of total": "percent of total",
        "pn": "pn",
        "_id": "_id",
    }
    for src, dst in alias_map.items():
        if src in df.columns:
            df = df.rename(columns={src: dst})

    # 3) Ensure the configured program column ends up as 'program' if needed
    incoming_prog = expected_program_header.strip().lower()
    if incoming_prog in df.columns and "program" not in df.columns:
        df = df.rename(columns={incoming_prog: "program"})
    # fallback from 'section' -> 'program'
    if "program" not in df.columns and "section" in df.columns:
        df = df.rename(columns={"section": "program"})

    # 4) Handle headers like "Total Items Selected using the On Demand Channel in 2023"
    on_demand_col = None
    for c in list(df.columns):
        if "total items selected" in c and "on demand" in c:
            on_demand_col = c
            break
    if on_demand_col:
        df = df.rename(columns={on_demand_col: "on_demand items selected"})

    # 5) Ensure required analytics columns exist (even if empty)
    must_exist = [
        "program",
        "items selected",
        "percent of total",
        "total items selected",
        "on_demand items selected",
        "channel",
        "title",
        "pn",
        "_id",
    ]
    for col in must_exist:
        if col not in df.columns:
            if col == "percent of total":
                df[col] = 0.0
            elif col in {"items selected", "total items selected", "on_demand items selected"}:
                df[col] = 0
            else:
                df[col] = ""

    # 6) Coerce numerics
    df["items selected"] = _coerce_numeric(df["items selected"])
    df["total items selected"] = _coerce_numeric(df["total items selected"])
    df["on_demand items selected"] = _coerce_numeric(df["on_demand items selected"])

    # Percent string -> float number (0–100)
    df["percent of total"] = (
        df["percent of total"].astype(str).replace("%", "", regex=False).str.strip()
    )
    df["percent of total"] = _coerce_numeric(df["percent of total"])

    # 7) Optional: enforce a consistent column order for the UI
    cols_order = [
        "program",
        "items selected",
        "total items selected",
        "on_demand items selected",
        "percent of total",
        "channel",
        "title",
        "pn",
        "_id",
    ]
    df = df[[c for c in cols_order if c in df.columns] + [c for c in df.columns if c not in cols_order]]

    return df

# === Per-year loader ===
@st.cache_data(ttl=300)
def load_year_df(year: str) -> pd.DataFrame:
    cfg = SHEETS[year]
    url = _csv_url(cfg["sheet_id"], gid=cfg.get("gid"))
    raw = pd.read_csv(url)
    df = _normalize_headers_and_columns(raw, expected_program_header=cfg["program_column"])

    if "program" not in df.columns:
        raise ValueError(
            "Could not find/normalize a program column in this sheet. "
            f"Expected something like '{cfg['program_column']}', 'program name', 'section name', or 'title'."
        )
    return df

# === Stacked (all years) loader ===
@st.cache_data(ttl=300)
def load_all_years() -> pd.DataFrame:
    """Load all years from Google Sheets and stack into one dataframe with a 'year' column."""
    frames: List[pd.DataFrame] = []
    for y in sorted(SHEETS.keys()):
        d = load_year_df(y).copy()
        d["year"] = y
        frames.append(d)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

def get_program_column(_: str) -> str:
    # Downstream code can always filter on this
    return "program"
