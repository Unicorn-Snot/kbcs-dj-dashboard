# Dj's Home Page
import unicodedata
import streamlit as st
import pandas as pd
import re
from typing import List, Union
from data_loader import SHEETS, load_year_df

PROGRAM_COL = "program"   # normalized from "Program Name"

# ---------- Helpers ----------
def _norm_text(s: str) -> str:
    """Normalize unicode, collapse spaces, lowercase, and unify apostrophes."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", str(s))
    s = s.replace("’", "'")             # curly -> straight apostrophe
    s = re.sub(r"\s+", " ", s)          # collapse multiple spaces
    return s.strip().casefold()


def _year_stack() -> pd.DataFrame:
    """Load all years and add a 'year' column."""
    frames = []
    for y in sorted(SHEETS.keys()):
        d = load_year_df(y).copy()
        d["year"] = y
        frames.append(d)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _filter_by_program(df: pd.DataFrame, show_name: str) -> pd.DataFrame:
    """
    Filter rows for this show:
      1) exact match on normalized 'program'
      2) fallback exact match on normalized 'pn'
      3) if no exact matches, return empty (caller may do fuzzy debug)
    """
    df = df.copy()
    df["program_norm"] = df.get("program", "").astype(str).map(_norm_text)
    df["pn_norm"] = df.get("pn", "").astype(str).map(_norm_text)

    choice_norm = _norm_text(show_name)

    view = df[df["program_norm"] == choice_norm]
    if not view.empty:
        return view

    view = df[df["pn_norm"] == choice_norm]
    return view  # may be empty; caller handles fuzzy/diagnostics


# ---------- KPI rendering ----------
def render_homepage(show_name: str, raw_view: pd.DataFrame, scope_label: str):
    """
    Render KPIs for a single show using the already-filtered rows (raw_view).
    Prefers per-program 'total items selected' when available; otherwise uses 'items selected'.
    """
    st.subheader(f"Your Program KPIs — {show_name}")

    cols_lower = {c.lower() for c in raw_view.columns}

    # Your Show Plays (prefer the per-program total column if present)
    total_items = None
    if "total items selected" in cols_lower:
        # if multiple rows per program (e.g., per month), max() gives the program's annual total in that sheet
        total_items = int(raw_view["total items selected"].max())
    elif "items selected" in cols_lower:
        # fallback: sum raw rows
        total_items = int(raw_view["items selected"].sum())
    else:
        total_items = 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Your Show Plays", total_items)

    # Share of Station Plays (use 'percent of total' if present)
    if "percent of total" in cols_lower and not raw_view["percent of total"].isna().all():
        share = float(raw_view["percent of total"].max())
        with c2:
            st.metric("Share of Station Plays", f"{share:.1f}%")

    # On‑Demand Plays (sum of normalized column if present)
    if "on_demand items selected" in cols_lower:
        on_demand = int(raw_view["on_demand items selected"].sum())
        with c3:
            st.metric("On‑Demand Plays", on_demand)

    st.caption(f"Scope: {scope_label}")
    st.markdown("---")

    # Breakdown by Channel (context)
    if {"channel", "items selected"}.issubset(cols_lower):
        by_ch = (
            raw_view.groupby(raw_view["channel"].astype(str).str.strip(), dropna=False)["items selected"]
                    .sum()
                    .sort_values(ascending=False)
        )
        if not by_ch.empty:
            st.caption("Where listeners are finding you (by Channel)")
            st.bar_chart(by_ch)

    # Top Titles (context)
    if {"title", "items selected"}.issubset(cols_lower):
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

    # Raw rows for this show (debug/inspection)
    with st.expander("Show raw rows (for this show)"):
        st.dataframe(raw_view, use_container_width=True)


# ---------- Top-level view ----------
def homepage_view_for_program(programs: Union[str, List[str]]):
    # Normalize to list
    programs = [programs] if isinstance(programs, str) else programs

    # Pick scope
    year_choice = st.radio(
        "Data scope",
        options=["All years"] + sorted(SHEETS.keys()),
        horizontal=True,
    )

    # Load data
    df = _year_stack() if year_choice == "All years" else load_year_df(year_choice)

    if PROGRAM_COL not in df.columns and "pn" not in df.columns:
        st.error("Neither 'program' nor 'pn' found. Check data_loader normalization.")
        return

    # Pick the DJ's show (if multiple)
    choice = programs[0] if len(programs) == 1 else st.selectbox("Select a program:", programs)

    # Filter for exact match (normalized)
    raw_view = _filter_by_program(df, choice)

    # If no exact match, offer a fuzzy diagnostic to help fix labels
    if raw_view.empty:
        choice_norm = _norm_text(choice)
        tmp = df.copy()
        tmp["program_norm"] = tmp.get("program", "").astype(str).map(_norm_text)
        tmp["pn_norm"] = tmp.get("pn", "").astype(str).map(_norm_text)

        # fuzzy contains search
        fuzzy = tmp[tmp["program_norm"].str.contains(re.escape(choice_norm), na=False)]
        if fuzzy.empty:
            fuzzy = tmp[tmp["pn_norm"].str.contains(re.escape(choice_norm), na=False)]

        st.warning(f"No exact rows found for '{choice}'. Showing possible matches below.")
        with st.expander("Possible matches (debug)"):
            st.write("Distinct program labels (normalized → sample originals):")
            samples = (
                tmp.assign(_prog_disp=tmp.get("program", "").fillna("").astype(str))
                   .groupby("program_norm", dropna=False)["_prog_disp"]
                   .apply(lambda s: list(s.head(3)))
                   .reset_index()
                   .rename(columns={"program_norm": "normalized", "_prog_disp": "examples"})
            )
            st.dataframe(samples, use_container_width=True)

            if "pn" in tmp.columns:
                st.write("Distinct PN labels (normalized → sample originals):")
                samples_pn = (
                    tmp.assign(_pn_disp=tmp.get("pn", "").fillna("").astype(str))
                       .groupby("pn_norm", dropna=False)["_pn_disp"]
                       .apply(lambda s: list(s.head(3)))
                       .reset_index()
                       .rename(columns={"pn_norm": "normalized", "_pn_disp": "examples"})
                )
                st.dataframe(samples_pn, use_container_width=True)

        # If you still want to render something, uncomment:
        # raw_view = fuzzy

        return

    # Year breakdown if viewing all years and totals column exists
    if year_choice == "All years" and "year" in raw_view.columns and "total items selected" in raw_view.columns:
        with st.expander("Year breakdown (Total Items Selected)"):
            yr = (
                raw_view.groupby("year", as_index=False)["total items selected"]
                        .max()
                        .sort_values("year")
            )
            if not yr.empty:
                st.bar_chart(yr.set_index("year"))

    # Render KPIs for this show
    scope_label = "All years" if year_choice == "All years" else year_choice
    render_homepage(choice, raw_view, scope_label)
