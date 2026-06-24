import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.embeds import EMBED_URLS, iframe_html

st.set_page_config(page_title="Men's College World Series | BMFB Data", page_icon="⚾", layout="wide")
st.markdown("<h1 style='text-align:center;'>⚾ Men's College World Series</h1>", unsafe_allow_html=True)
components.html(
    iframe_html(EMBED_URLS["mcws"], height_px=1100, top_offset_px=120,
                title="Men's College World Series - live Excel workbook"),
    height=1100, scrolling=False,
)
st.markdown("<p style='text-align:center;color:#555;'>Updates automatically when the Excel file is saved in OneDrive.</p>", unsafe_allow_html=True)
