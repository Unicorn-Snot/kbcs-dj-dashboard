import streamlit as st
from dj_access_map import dj_access_map
from dj_homepage import render_homepage
from data_loader import SHEETS, load_year_df

st.set_page_config(page_title="KBCS DJ Dashboard", layout="wide")

# 1) Define once, before use
CANVA_URL = "https://www.canva.com/design/DAGwp9keuCM/sVuvLE-Coyxg-RxMtHvfWQ/view?embed"


# 2) Canva iframe as the visual login page (single embed)
st.components.v1.iframe(CANVA_URL, height=700, scrolling=True)

# 3) Overlay CSS (keep your style; just ensure z-index is above iframe)
st.markdown("""
<style>
/* Wrapper that matches iframe dimensions */
.overlay-stage {
  position: relative;
  height: 700px;   /* same as iframe height */
}

/* Place login boxes ON TOP of the iframe */
.overlay-name, .overlay-code, .overlay-button {
  position: absolute;
  z-index: 10;   /* sits above iframe */
  width: 380px;  /* adjust width to match white box */
  left: 520px;   /* <-- adjust this until it lines up with your Canva box */
}

/* Adjust vertical positions */
.overlay-name { top: 220px; }
.overlay-code { top: 300px; }
.overlay-button { top: 380px; }

</style>
""", unsafe_allow_html=True)

# 4) Login inputs (form = better submit semantics)
st.markdown('<div class="overlay-stage">', unsafe_allow_html=True)
st.components.v1.iframe(CANVA_URL, height=700, scrolling=False)

# Login form (inside overlay-stage)
with st.form("dj_login_form", clear_on_submit=False):
    st.markdown('<div class="overlay-name">', unsafe_allow_html=True)
    input_name = st.text_input("What's your name?", key="dj_name", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="overlay-code">', unsafe_allow_html=True)
    input_code = st.text_input("Access Code", type="password", key="dj_code", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
    submitted = st.form_submit_button("Enter")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close overlay-stage

# 5) Auth + year picker happens AFTER login succeeds
if submitted:
    key = (input_name.strip(), input_code.strip())
    programs = dj_access_map.get(key)

    if programs:
        st.success(f"Welcome {input_name}! Loading KPIs for: {programs}")

        # Let the DJ choose which year dataset to view (because your sheets are per-year)
        year = st.selectbox("Year", list(SHEETS.keys()))
        df = load_year_df(year)              # normalized df with 'program' column

        # Render KPIs for their program(s)
        render_homepage(programs, df)
    else:
        st.error("Access Denied. Please check your name and access code.")

        
