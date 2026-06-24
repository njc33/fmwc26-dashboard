import os

EMBED_URLS = {
    "mcws": os.environ.get(
        "EMBED_MCWS",
        "https://1drv.ms/x/c/13C7E9465F9473DD/IQTqHyCCQIPGQ4OvFquRDo2NAQPbtzzojDtLmMTudQod-oI",
    ),
    "fifa": os.environ.get("EMBED_FIFA", ""),
    "future_gms": os.environ.get("EMBED_FUTURE_GMS", ""),
    "naffl": os.environ.get("EMBED_NAFFL", ""),
}

def iframe_html(src, height_px=1100, top_offset_px=120, title="Embedded content"):
    if not src:
        return (
            "<p style='color:#888;text-align:center;padding:2rem;'>"
            "Embed URL not configured. Set the appropriate environment variable.</p>"
        )
    return f"""
<style>
:root {{ --top-offset: {top_offset_px}px; }}
html, body {{ margin:0; padding:0; height:100%; }}
.embed-full {{
  width:100vw; max-width:100%;
  height:calc(100vh - var(--top-offset));
  display:flex; align-items:stretch; justify-content:center;
  background:#fff; box-sizing:border-box; padding:0; margin:0 auto;
}}
.embed-full iframe {{ width:100%; height:100%; border:0; display:block; }}
</style>
<div class="embed-full">
  <iframe src="{src}" title="{title}" frameborder="0" scrolling="no"
    sandbox="allow-same-origin allow-scripts allow-forms allow-popups"></iframe>
</div>
"""
