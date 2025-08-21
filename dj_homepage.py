# Dj's Home Page
import streamlit as st
import pandas as pd
from typing import List, Union

PROGRAM_COL = "program"   # unified by data_loader

def render_homepage(programs: Union[str, List[str]], df: pd.DataFrame):
    if isinstance(programs, str):
        programs = [programs]

    st.subheader("Your Program KPIs")

    choice = programs[0] if len(programs) == 1 else st.selectbox("Select a program:", programs)

    if PROGRAM_COL not in df.columns:
        st.error(f"Column '{PROGRAM_COL}' not found in data.")
        return

    program_df = df[df[PROGRAM_COL] == choice]
    if program_df.empty:
        st.warning(f"No rows found for program: {choice}")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Items Selected", int(program_df.get("items selected", pd.Series([0])).sum()))
    with col2:
        st.metric("Unique Users", int(program_df.get("unique users", pd.Series([0])).sum()))
    with col3:
        st.metric("Sessions", int(program_df.get("sessions", pd.Series([0])).sum()))

    if "date" in program_df.columns:
        tmp = program_df.copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"]).sort_values("date")
        if "items selected" in tmp.columns:
            st.line_chart(tmp.set_index("date")["items selected"])

    with st.expander("Show raw rows"):
        st.dataframe(program_df)

