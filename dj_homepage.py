# Dj's Home Page
import streamlit as st
import pandas as pd
from typing import List, Union
from data_loader import SHEETS, load_year_df

PROGRAM_COL = "program"   # unified by data_loader

def load_merged_years() -> pd.DataFrame:
    """Load all years from Google Sheets and stack into one long dataframe with a 'year' column."""
    frames = []
    for y in sorted(SHEETS.keys()):
        d = load_year_df(y).copy()
        d["year"] = y
        frames.append(d)
    if not frames:
        return pd.DataFrame()
    df_all = pd.concat(frames, ignore_index=True)
    return df_all

def render_homepage(programs, df: pd.DataFrame):
    # Normalize to a single program name for header
    program_name = programs[0] if isinstance(programs, list) else programs
    st.subheader(f"Your Program KPIs{f' — {program_name}' if program_name else ''}")

    cols = {c.lower() for c in df.columns}

    # 1) Host Show Plays → sum of Items Selected
    total_items = int(df.get("items selected", 0).sum())
    st.metric("Your Show Plays", total_items)

    # 2) Share of Station Plays → from % of Total (preferred) or fallback using totals
    if "percent of total" in cols:
        share = float(df["percent of total"].mean())  # % already in sheet
        st.metric("Share of Station Plays", f"{share:.1f}%")
    elif {"items selected", "total items selected"}.issubset(cols):
        station_total = float(df["total items selected"].max())
        share = (total_items / station_total * 100.0) if station_total > 0 else 0.0
        st.metric("Share of Station Plays", f"{share:.1f}%")

    # 3) On-Demand Plays (if present)
    if "on_demand items selected" in cols:
        on_demand = int(df["on_demand items selected"].sum())
        st.metric("On-Demand Plays", on_demand)

    st.markdown("---")

    # 4) Breakdown by Channel (if Channel exists)
    if "channel" in cols:
        by_ch = (
            df.groupby(df["channel"].astype(str).str.strip(), dropna=False)["items selected"]
              .sum()
              .sort_values(ascending=False)
        )
        if not by_ch.empty:
            st.caption("Where listeners are finding you (by Channel)")
            st.bar_chart(by_ch)

    # 5) Top Titles (if Title exists)
    if "title" in cols:
        top_titles = (
            df.groupby(df["title"].astype(str).str.strip(), dropna=False)["items selected"]
              .sum()
              .sort_values(ascending=False)
              .head(10)
              .reset_index()
        )
        if not top_titles.empty:
            st.caption("Top 10 Pieces Your Listeners Selected Most")
            st.dataframe(
                top_titles.rename(columns={
                    "title": "Title",
                    "items selected": "Plays"
                }),
                use_container_width=True
            )

    # 6) Raw view
    with st.expander("Show raw rows"):
        st.dataframe(df, use_container_width=True)

def homepage_view_for_program(programs: Union[str, List[str]]):
    """UI for year picker (All years or single), filtering, and passing to render_homepage()."""
    # Normalize to list
    if isinstance(programs, str):
        programs = [programs]

    # 1) Let the DJ choose scope: All years vs a specific year
    year_choice = st.radio(
        "Data scope",
        options=["All years"] + sorted(SHEETS.keys()),
        horizontal=True,
    )

    # 2) Load the right dataframe
    if year_choice == "All years":
        df = load_merged_years()
    else:
        df = load_year_df(year_choice)

    # 3) Safety: ensure expected column
    if PROGRAM_COL not in df.columns:
        st.error(f"Column '{PROGRAM_COL}' not found in the data. Check data_loader normalization.")
        return

    # 4) If a DJ has multiple programs, let them pick which one to view
    choice = programs[0] if len(programs) == 1 else st.selectbox("Select a program:", programs)

    # 5) Filter rows for that program
    view = df[df[PROGRAM_COL] == choice]

    if view.empty:
        st.warning(f"No rows found for program: {choice} in scope: {year_choice}")
        return

    # 6) If All years: let them optionally facet by year
    if year_choice == "All years" and "year" in view.columns:
        with st.expander("Year breakdown (quick view)"):
            # Small pivot to see Items Selected per year (adjust columns if differ)
            if "items selected" in view.columns:
                yr = (view[["year", "items selected"]]
                      .groupby("year", as_index=False)["items selected"].sum()
                      .sort_values("year"))
                st.bar_chart(yr.set_index("year"))

    # 7) Hand off to existing KPI renderer
    render_homepage(choice, view)
