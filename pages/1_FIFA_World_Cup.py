import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.embeds import EMBED_URLS, iframe_html

st.set_page_config(page_title="FIFA World Cup 2026 | BMFB Data", page_icon="⚽", layout="wide")
st.markdown("<h1 style='text-align:center;'>⚽ 2026 FIFA Men's World Cup</h1>", unsafe_allow_html=True)

if EMBED_URLS["fifa"]:
    components.html(iframe_html(EMBED_URLS["fifa"], title="FIFA World Cup 2026"), height=1100, scrolling=False)
else:
    st.info("Set EMBED_FIFA in Render environment variables to activate this section.", icon="ℹ️")
    st.write("The 2026 FIFA Men's World Cup is hosted by the USA, Canada, and Mexico.")
