# Dj's Home Page

import streamlit as st
import pandas as pd
from typing import List, Union
from data_loader import SHEETS, load_year_df

PROGRAM_COL = "program"   # normalized from "Program Name"

def _filter_for_show(df: pd.DataFrame, show_name: str) -> pd.DataFrame:
    """Filter rows for this show; prefer 'program' but fall back to 'pn' when needed."""
    cols = {c.lower() for c in df.columns}
    if PROGRAM_COL in cols:
        view = df[df[PROGRAM_COL].astype(str).str.strip() == show_name]
        if not view.empty:
            return view
    if "pn" in cols:
        return df[df["pn"].astype(str).str.strip() == show_name]
    return df.iloc[0:0]  # empty

def _pick_program_row(view: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce to a single row representing the program’s totals.
    We choose the row with the largest 'total items selected'
    (safe if there are duplicates or per-month rows).
    """
    if "total items selected" in {c.lower() for c in view.columns} and not view.empty:
        return view.sort_values("total items selected", ascending=False).head(1)
    # Fallback: if totals column is missing, keep as-is (the KPI code will fall back)
    return view.head(1)

def render_homepage(programs: Union[str, List[str]], df: pd.DataFrame):
    # Normalize to a single program name for header
    show_name = programs[0] if isinstance(programs, list) else programs
    st.subheader(f"Your Program KPIs{f' — {show_name}' if show_name else ''}")

    # 1) Filter to this show (by Program Name, fallback PN)
    raw_view = _filter_for_show(df, show_name)
    if raw_view.empty:
        st.warning(f"No rows found for program: {show_name}")
        return

    # 2) Collapse to a single “program total” row (uses Total Items Selected)
    view = _pick_program_row(raw_view)
    cols = {c.lower() for c in view.columns}

    # 3) Your Show Plays → use Total Items Selected (definitive)
    if "total items selected" in cols:
        total_items = int(view["total items selected"].iloc[0])
    else:
        # graceful fallback if an older sheet lacks totals
        total_items = int(raw_view.get("items selected", pd.Series([0])).sum())
    st.metric("Your Show Plays", total_items)

    # 4) Share of Station Plays → use Percent of Total if present
    if "percent of total" in cols:
        share = float(view["percent of total"].iloc[0])
        st.metric("Share of Station Plays", f"{share:.1f}%")
    else:
        # optional fallback if you later want to compute from a known station total
        pass

    # 5) On‑Demand Plays → use the per‑program total (not a global sum)
    if "on_demand items selected" in cols:
        on_demand = int(view["on_demand items selected"].iloc[0])
        st.metric("On‑Demand Plays", on_demand)

    st.markdown("---")

    # 6) Channel breakdown (context only; sums Items Selected within this show’s rows)
    if "channel" in cols and "items selected" in {c.lower() for c in raw_view.columns}:
        by_ch = (
            raw_view.groupby(raw_view["channel"].astype(str).str.strip(), dropna=False)["items selected"]
                   .sum()
                   .sort_values(ascending=False)
        )
        if not by_ch.empty:
            st.caption("Where listeners are finding you (by Channel)")
            st.bar_chart(by_ch)

    # 7) Top Titles (context only)
    if "title" in cols and "items selected" in {c.lower() for c in raw_view.columns}:
        top_titles = (
            raw_view.groupby(raw_view["title"].astype(str).str.strip(), dropna=False)["items selected"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
        )
        if not top_titles.empty:
            st.caption("Top 10 Pieces Your Listeners Selected Most")
            st.dataframe(
                top_titles.rename(columns={"title": "Title", "items selected": "Plays"}),
                use_container_width=True
            )

    # 8) Raw rows (for this show)
    with st.expander("Show raw rows (for this show)"):
        st.dataframe(raw_view, use_container_width=True)

def load_merged_years() -> pd.DataFrame:
    frames = []
    for y in sorted(SHEETS.keys()):
        d = load_year_df(y).copy()
        d["year"] = y
        frames.append(d)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def homepage_view_for_program(programs: Union[str, List[str]]):
    # Normalize to list
    programs = [programs] if isinstance(programs, str) else programs

    year_choice = st.radio("Data scope", options=["All years"] + sorted(SHEETS.keys()), horizontal=True)

    df = load_merged_years() if year_choice == "All years" else load_year_df(year_choice)

    if PROGRAM_COL not in df.columns and "pn" not in df.columns:
        st.error("Neither 'program' nor 'pn' found. Check data_loader normalization.")
        return

    choice = programs[0] if len(programs) == 1 else st.selectbox("Select a program:", programs)

    # Year breakdown (for this show) using the total column
    view_all = _filter_for_show(df, choice)
    if year_choice == "All years" and not view_all.empty and "total items selected" in {c.lower() for c in view_all.columns}:
        with st.expander("Year breakdown (Total Items Selected)"):
            # If multiple rows per year, take the max per year to reflect the program’s annual total
            yr = (
                view_all.groupby("year", as_index=False)["total items selected"]
                        .max()
                        .sort_values("year")
            )
            st.bar_chart(yr.set_index("year"))

    render_homepage(choice, df)
