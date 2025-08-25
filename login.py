import streamlit as st
from dj_access_map import dj_access_map
from dj_homepage import homepage_view_for_program
from data_loader import SHEETS, load_year_df

st.set_page_config(page_title="KBCS DJ Dashboard", layout="wide")

CANVA_URL = "https://www.canva.com/design/DAGwp9keuCM/sVuvLE-Coyxg-RxMtHvfWQ/view?embed"

# --- Canva background ---
st.markdown(f"""
    <style>
    .stApp {{
        background: transparent !important;
    }}

    .canva-bg {{
        position: fixed;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        border: none;
        z-index: -3;
    }}

    .shade {{
        position: fixed;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, .65);
        backdrop-filter: blur(6px);
        z-index: -2;
    }}

    .overlay {{
        position: relative;
        top: 210px;
        left: -35%;
        height: 50px;  /* forces a set vertical length */
        padding: 30px 25px;
        margin: 150px auto;
        width: 500px;
        padding: 20px;
        background: rgba(0,0,0,0.6);
        border-radius: 10px;
        z-index: -3;
    }}
    
    .login-label {{
        font-size: 45px;
        color: white;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    </style>

    <iframe class="canva-bg" src="{CANVA_URL}" allowfullscreen></iframe>
""", unsafe_allow_html=True)

# --- Login form overlay ---
with st.container():
    st.markdown('<div class="overlay">', unsafe_allow_html=True)

    st.markdown('<div class="login-label">What’s your name?</div>', unsafe_allow_html=True)
    input_name = st.text_input("", key="name_input")

    st.markdown('<div class="login-label">Access Code</div>', unsafe_allow_html=True)
    input_code = st.text_input("", type="password", key="access_code_input")

    submitted = st.button("Enter")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Auth logic ---
if submitted:
    key = (input_name.strip(), input_code.strip())
    programs = dj_access_map.get(key)

    if programs:
        st.success(f"Welcome {input_name}! Loading KPIs for: {programs}")
        homepage_view_for_program(programs)
    else:
        st.error("Access Denied. Please check your name and access code.")
