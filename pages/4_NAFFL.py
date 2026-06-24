import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.embeds import EMBED_URLS, iframe_html

st.set_page_config(page_title="NAFFL | BMFB Data", page_icon="🏈", layout="wide")
st.markdown("<h1 style='text-align:center;'>🏈 NAFFL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#555;'>North American Flag Football League</p>", unsafe_allow_html=True)

if EMBED_URLS["naffl"]:
    components.html(iframe_html(EMBED_URLS["naffl"], title="NAFFL data"), height=1100, scrolling=False)
else:
    st.info("Set EMBED_NAFFL in Render environment variables to activate this section.", icon="ℹ️")
    st.write("NAFFL scores, standings, and schedule will appear here once configured.")
