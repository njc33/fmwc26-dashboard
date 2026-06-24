# app.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2026 FIFA Men's World Cup", layout="wide")
st.title("2026 FIFA Men's World Cup")

# === OneDrive direct-download link (corrected) ===
embed_src = "https://onedrive.live.com/download?resid=13C7E9465F9473DD!IQDqHyCCQIPGQ4OvFquRDo2NAcFaXizA-17m1OFlf68Hc-A&authkey=!nzgder"

# === UI controls ===
st.sidebar.header("View controls")
zoom = st.sidebar.slider("Zoom (scale)", min_value=50, max_value=150, value=100, step=5)
offset_x = st.sidebar.slider("Horizontal offset (px)", min_value=-2000, max_value=2000, value=0, step=10)
offset_y = st.sidebar.slider("Vertical offset (px)", min_value=-2000, max_value=2000, value=0, step=10)
container_width = st.sidebar.number_input("Viewport width (px)", min_value=400, max_value=3000, value=1200, step=50)
container_height = st.sidebar.number_input("Viewport height (px)", min_value=200, max_value=2000, value=700, step=25)

hide_guides = st.sidebar.checkbox("Hide row/column guides (overlay)", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Tips:\n\n"
    "- Use **Zoom** to scale the embedded workbook.\n"
    "- Use **offset** sliders to align the visible area with A1:BA105.\n"
    "- If the embed appears blank, open the OneDrive link in a new tab to confirm access."
)

# === Compute CSS transform values ===
scale = zoom / 100.0
translate_x = int(offset_x)
translate_y = int(offset_y)
width_px = int(container_width)
height_px = int(container_height)

guide_left_width = 60
guide_top_height = 28

html = f"""
<style>
:root {{
  --container-w: {width_px}px;
  --container-h: {height_px}px;
  --iframe-w: 2000px;
  --iframe-h: 1400px;
  --translate-x: {translate_x}px;
  --translate-y: {translate_y}px;
  --scale: {scale};
  --guide-left: {guide_left_width}px;
  --guide-top: {guide_top_height}px;
}}
.embed-wrap {{
  width: var(--container-w);
  height: var(--container-h);
  overflow: hidden;
  border: 1px solid #ddd;
  margin: 8px auto;
  position: relative;
  background: #ffffff;
}}
.embed-wrap iframe {{
  width: var(--iframe-w);
  height: var(--iframe-h);
  border: 0;
  transform-origin: 0 0;
  transform: translate(calc(var(--translate-x) * 1px), calc(var(--translate-y) * 1px)) scale(var(--scale));
  -webkit-transform-origin: 0 0;
  -webkit-transform: translate(calc(var(--translate-x) * 1px), calc(var(--translate-y) * 1px)) scale(var(--scale));
  pointer-events: auto;
  display: block;
}}
.overlay-top {{
  position: absolute;
  left: 0;
  top: 0;
  height: var(--guide-top);
  width: 100%;
  background: #ffffff;
  z-index: 9999;
  pointer-events: none;
}}
.overlay-left {{
  position: absolute;
  left: 0;
  top: 0;
  width: var(--guide-left);
  height: 100%;
  background: #ffffff;
  z-index: 9999;
  pointer-events: none;
}}
.embed-wrap::after {{
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.06);
  pointer-events: none;
}}
</style>

<div style="text-align:center; max-width:100%;">
  <div class="embed-wrap" id="embedWrap">
    <iframe src="{embed_src}" sandbox="allow-same-origin allow-scripts allow-forms allow-popups" scrolling="no"></iframe>
    {"<div class='overlay-top'></div>" if hide_guides else ""}
    {"<div class='overlay-left'></div>" if hide_guides else ""}
  </div>
</div>
"""

components.html(html, height=height_px + 40, scrolling=False)

st.markdown(
    "If the visible area doesn't perfectly match A1:BA105, adjust **Zoom** and the **offset** sliders until the top-left of the workbook aligns with the container."
)
