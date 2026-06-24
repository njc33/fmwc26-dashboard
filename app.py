import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2026 FIFA Men's World Cup", layout="wide")

# === Page Title ===
st.markdown(
    "<h1 style='text-align: center; margin: 8px 0 12px;'>2026 FIFA Men's World Cup</h1>",
    unsafe_allow_html=True
)

# === OneDrive EMBED (your provided iframe src) ===
embed_src = "https://1drv.ms/x/c/13C7E9465F9473DD/IQTqHyCCQIPGQ4OvFquRDo2NAQPbtzzojDtLmMTudQod-oI"

# === Full-page responsive embed ===
# The iframe is sized to fill nearly the entire viewport height while leaving room for the Streamlit header.
html = f"""
<style>
:root {{
  --top-offset: 120px; /* space for title/Streamlit chrome; adjust if needed */
}}
html, body {{
  margin: 0;
  padding: 0;
  height: 100%;
}}
.embed-full {{
  width: 100vw;
  max-width: 100%;
  height: calc(100vh - var(--top-offset));
  display: flex;
  align-items: stretch;
  justify-content: center;
  background: #fff;
  box-sizing: border-box;
  padding: 0;
  margin: 0 auto;
}}
.embed-full iframe {{
  width: 100%;
  height: 100%;
  border: 0;
  display: block;
}}
/* Remove extra Streamlit padding around the component when possible */
.stApp > main > div[role="main"] {{
  padding-top: 6px;
}}
</style>

<div class="embed-full">
  <iframe src="{embed_src}" frameborder="0" scrolling="no" sandbox="allow-same-origin allow-scripts allow-forms allow-popups"></iframe>
</div>
"""

# components.html requires a numeric height; set it high enough so Streamlit allocates ample space.
# The iframe itself uses calc(100vh - top-offset) so it will visually fill the page.
components.html(html, height=1100, scrolling=False)

st.markdown(
    "<p style='text-align:center; margin-top:10px;'>This live workbook updates automatically whenever the Excel file is updated in OneDrive.</p>",
    unsafe_allow_html=True
)
