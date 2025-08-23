import streamlit as st
from dj_access_map import dj_access_map
from dj_homepage import homepage_view_for_program

st.set_page_config(page_title="KBCS DJ Dashboard", layout="wide")

CANVA_URL = "https://www.canva.com/design/DAGwp9keuCM/sVuvLE-Coyxg-RxMtHvfWQ/view?embed"

# --- init session state
if "authed" not in st.session_state:
    st.session_state.authed = False
if "programs" not in st.session_state:
    st.session_state.programs = None
if "dj_name" not in st.session_state:
    st.session_state.dj_name = ""

# --- if already authed, skip login UI
if st.session_state.authed and st.session_state.programs:
    st.success(f"Welcome {st.session_state.dj_name}! Loading KPIs for: {st.session_state.programs}")
    homepage_view_for_program(st.session_state.programs)
    st.stop()

# ---------- LOGIN UI ----------
# Overlay CSS
st.markdown("""
<style>
.overlay-stage { position: relative; height: 700px; }
.overlay-name, .overlay-code, .overlay-button {
  position: absolute; z-index: 10; width: 380px; left: 520px;
}
.overlay-name { top: 220px; }
.overlay-code { top: 300px; }
.overlay-button { top: 380px; }
</style>
""", unsafe_allow_html=True)

# Single iframe + positioned overlays
st.markdown('<div class="overlay-stage">', unsafe_allow_html=True)
st.components.v1.iframe(CANVA_URL, height=700, scrolling=False)

with st.form("dj_login_form", clear_on_submit=False):
    st.markdown('<div class="overlay-name">', unsafe_allow_html=True)
    input_name = st.text_input("What's your name?", key="dj_name_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="overlay-code">', unsafe_allow_html=True)
    input_code = st.text_input("Access Code", type="password", key="dj_code_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
    submitted = st.form_submit_button("Enter")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close overlay-stage

# Auth check
if submitted:
    name = (input_name or "").strip()
    code = (input_code or "").strip()

    # exact match; if you prefer case-insensitive names, uncomment next line
    # name_key = name.lower()
    # build a case-insensitive mapping if desired:
    # norm_map = { (k[0].lower(), k[1]): v for k,v in dj_access_map.items() }
    # programs = norm_map.get((name_key, code))

    programs = dj_access_map.get((name, code))
    if programs:
        st.session_state.authed = True
        st.session_state.programs = programs
        st.session_state.dj_name = name
        st.rerun()  # jump into the authed view immediately
    else:
        st.error("Access Denied. Please check your name and access code.")
