import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2026 FIFA Men's World Cup", layout="wide")

# === Page Title ===
st.markdown(
    "<h1 style='text-align: center; margin-bottom: 10px;'>2026 FIFA Men's World Cup</h1>",
    unsafe_allow_html=True
)

# === OneDrive EMBED (from your iframe) ===
embed_src = "https://1drv.ms/x/c/13C7E9465F9473DD/IQTqHyCCQIPGQ4OvFquRDo2NAQPbtzzojDtLmMTudQod-oI"
# dimensions from the iframe you provided
container_width = 402
container_height = 346

# === Clean embed (using the exact iframe attributes you provided) ===
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
  display: block;
}}
</style>

<div style="text-align:center; max-width:100%;">
  <div class="embed-wrap">
    <iframe src="{embed_src}" width="{container_width}" height="{container_height}" frameborder="0" scrolling="no" allowfullscreen></iframe>
  </div>
</div>
"""

components.html(html, height=container_height + 40, scrolling=False)

st.markdown(
    "<p style='text-align:center;'>This live workbook updates automatically whenever the Excel file is updated in OneDrive.</p>",
    unsafe_allow_html=True
)
