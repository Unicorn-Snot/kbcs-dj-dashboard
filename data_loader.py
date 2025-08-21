# load data from Google Sheet
import streamlit as st
from urllib.parse import quote
import pandas as pd
from typing import Optional, Dict

# organize my three google sheets by year for scaling
SHEETS : Dict[str, Dict[str, str]] = {
    "2022":{
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
        "sheet_id": "1wh65x9uwfQHDGax0xhR_Q2tZSdfyBlLMw3gMlTXIZl0",
        "gid": "1807168814",
        "program_column": "Program Name",
    },
}

def _csv_url(sheet_id: str, gid: Optional[str] = None, tab: Optional[str] = None) -> str:
    if gid:
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    if tab:
        from urllib.parse import quote
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={quote(tab)}"
    raise ValueError("Provide either gid or tab")

# refresh every 5 minutes
@st.cache_data(ttl=300)
def load_year_df(year: str) -> pd.DataFrame:
    cfg = SHEETS[year]
    url = _csv_url(cfg["sheet_id"], gid=cfg.get("gid"))
    df = pd.read_csv(url)

    # normalize headers
    df.columns = df.columns.str.strip().str.lower()

    src = cfg["program_column"].strip().lower()
    if src != "program" and src in df.columns:
        df = df.rename(columns={src: "program"})
    elif "title" in df.columns and "program" not in df.columns:
        # fallback if a sheet only has Title
        df = df.rename(columns={"title": "program"})

    # 3) safety check
    if "program" not in df.columns:
        raise ValueError(
            "Could not find a program column in this sheet. "
            f"Expected '{cfg['program_column']}', or a fallback like 'Title'."
        )

    return df

def get_program_column(_: str) -> str:
    # Downstream code can always filter on this
    return "program"
