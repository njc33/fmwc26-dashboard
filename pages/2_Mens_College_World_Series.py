import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.embeds import EMBED_URLS

st.set_page_config(page_title="Men's College World Series | BMFB Data", page_icon="⚾", layout="wide")
st.markdown("<h1 style='text-align:center;'>⚾ Men's College World Series</h1>", unsafe_allow_html=True)

# Build a clean iframe using only the embed src (no sandbox, no extra title fragment)
iframe_src = EMBED_URLS["mcws"]

iframe_html = f'''
<iframe
  src="{iframe_src}"
  width="100%"
  height="1600"
  frameborder="0"
  scrolling="no"
  title="Men's College World Series workbook">
</iframe>
'''

# Render the iframe; set the Streamlit component height to match the iframe height
components.html(iframe_html, height=1600, scrolling=False)

st.markdown("<p style='text-align:center;color:#555;'>Updates automatically when the Excel file is saved in OneDrive.</p>", unsafe_allow_html=True)
