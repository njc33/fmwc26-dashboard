import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2026 FIFA Men's World Cup", layout="wide")
st.title("2026 FIFA Men's World Cup")

# === OneDrive EMBED LINK (this one works for iframe embedding) ===
embed_src = "https://1drv.ms/x/c/13C7E9465F9473DD/IQT8CnkpzF0wQ75QWftP-BC8AboZVps3bpDok7h1RQCo8_M"

# === Fixed viewport size for the embedded workbook ===
container_width = 1200
container_height = 700

# === CSS + HTML for clean embed (no controls, no overlays) ===
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
    "This live workbook updates automatically whenever the Excel file is updated in OneDrive."
)
