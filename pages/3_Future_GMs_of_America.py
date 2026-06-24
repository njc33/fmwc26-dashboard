import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.embeds import EMBED_URLS, iframe_html

st.set_page_config(page_title="Future GMs of America | BMFB Data", page_icon="🧢", layout="wide")
st.markdown("<h1 style='text-align:center;'>🧢 Future GMs of America</h1>", unsafe_allow_html=True)

if EMBED_URLS["future_gms"]:
    components.html(iframe_html(EMBED_URLS["future_gms"], title="Future GMs of America"), height=1100, scrolling=False)
else:
    st.info("Set EMBED_FUTURE_GMS in Render environment variables to activate this section.", icon="ℹ️")
    st.write("Prospect rankings, draft boards, and GM simulation data will appear here.")
