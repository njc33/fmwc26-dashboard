# app.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2026 FIFA Men's World Cup", layout="wide")
st.title("2026 FIFA Men's World Cup")

# === User-editable embed src (paste your OneDrive embed src here) ===
embed_src = "https://1drv.ms/x/c/13C7E9465F9473DD/IQT8CnkpzF0wQ75QWftP-BC8AboZVps3bpDok7h1RQCo8_M"

# === UI controls ===
st.sidebar.header("View controls")
zoom = st.sidebar.slider("Zoom (scale)", min_value=50, max_value=150, value=100, step=5)
# Offsets let you nudge the visible window to align A1:BA105 precisely
offset_x = st.sidebar.slider("Horizontal offset (px)", min_value=-2000, max_value=2000, value=0, step=10)
offset_y = st.sidebar.slider("Vertical offset (px)", min_value=-2000, max_value=2000, value=0, step=10)
# Container size approximating A1:BA105 viewport; user can tweak
container_width = st.sidebar.number_input("Viewport width (px)", min_value=400, max_value=3000, value=1200, step=50)
container_height = st.sidebar.number_input("Viewport height (px)", min_value=200, max_value=2000, value=700, step=25)

# Toggle to hide the Excel row/column guides by overlaying masks
hide_guides = st.sidebar.checkbox("Hide row/column guides (overlay)", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Tips:\n\n"
    "- Use **Zoom** to scale the embedded workbook.\n"
    "- Use **offset** sliders to nudge the workbook so the visible area matches A1:BA105.\n"
    "- If the embed appears blank, open the OneDrive link in a new tab to confirm access."
)

# === Compute CSS transform values ===
scale = zoom / 100.0
# We will translate the iframe by (-offset_x, -offset_y) before scaling.
# Because transform order matters, we apply translate then scale with transform-origin top left.
translate_x = int(offset_x)
translate_y = int(offset_y)

# These values control how much of the workbook is visible.
# The container clips everything outside its bounds, enforcing the A1:BA105 restriction visually.
width_px = int(container_width)
height_px = int(container_height)

# Header/guide overlay sizes (approximate). Adjust via CSS if needed.
# These overlay boxes hide the Excel Online column letters and row numbers visually.
guide_left_width = 60   # width of the left guide (rows)
guide_top_height = 28   # height of the top guide (columns)

# Build the HTML with inline CSS. The iframe is larger than the container and translated/scaled.
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
/* center container */
.embed-wrap {{
  width: var(--container-w);
  height: var(--container-h);
  overflow: hidden;
  border: 1px solid #ddd;
  margin: 8px auto;
  position: relative;
  background: #ffffff;
}}

/* iframe is positioned and transformed so only the desired rectangle shows */
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

/* overlay to hide the top column letters */
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

/* overlay to hide the left row numbers */
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

/* small visual border to show the clipped area */
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

<script>
/* Allow keyboard arrow nudges for fine adjustments (optional) */
document.addEventListener('keydown', function(e) {{
  // Arrow keys nudge offsets by 10px; Shift + arrow nudges by 50px
  const step = e.shiftKey ? 50 : 10;
  if (e.key === 'ArrowLeft') {{
    // send message to Streamlit to update offset_x (no direct comm here)
  }}
  // Note: Streamlit cannot be updated from this iframe script directly without Streamlit JS API.
}});
</script>
"""

# Render the HTML
components.html(html, height=height_px + 40, scrolling=False)

st.markdown(
    "If the visible area doesn't perfectly match A1:BA105, adjust **Zoom** and the **offset** sliders until the top-left of the workbook aligns with the container. "
    "The overlay hides the Excel Online row/column guides visually; users can still open the workbook in a new tab if they have access."
)
