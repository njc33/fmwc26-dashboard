import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2026 FIFA Men's World Cup", layout="wide")

# === Page Title ===
st.markdown(
    "<h1 style='text-align: center; margin-bottom: 10px;'>2026 FIFA Men's World Cup</h1>",
    unsafe_allow_html=True
)

# === OneDrive EMBED LINK (working embed link) ===
embed_src = "https://1drv.ms/x/c/13C7E9465F9473DD/IQDqHyCCQIPGQ4OvFquRDo2NAcFaXizA-17m1OFlf68Hc-A?e=HWgmjs"

# === Fixed viewport size for the embedded workbook ===
container_width = 1200
container_height = 700

# === Clean embed (no controls, no sidebar) ===
html = f"""
<style>
.embed-wrap {{
  width: {container_width}px;
  height: {container_height}px;
  overflow: hidden;
  border: 1px solid #ddd;
  margin: 20px auto;
  background: #ffffff;
}}
.embed-wrap iframe {{
  width: 100%;
  height: 100%;
  border: 0;
}}
</style>

<div style="text-align:center; max-width:100%;">
  <div class="embed-wrap">
    <iframe src="{embed_src}" sandbox="allow-same-origin allow-scripts allow-forms allow-popups"></iframe>
  </div>
</div>
"""

components.html(html, height=container_height + 40, scrolling=False)

st.markdown(
    "<p style='text-align:center;'>This live workbook updates automatically whenever the Excel file is updated in OneDrive.</p>",
    unsafe_allow_html=True
)
