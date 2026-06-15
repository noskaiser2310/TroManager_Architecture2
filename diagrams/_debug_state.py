"""Debug: check SVG attributes and inner content."""
from playwright.sync_api import sync_playwright

mmd = open("diagrams/02_react_state.mmd").read()

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>body{{margin:0;padding:0;background:white}} svg{{max-width:none!important;display:block}}</style>
</head><body>
<pre class="mermaid">{mmd}</pre>
<script>
mermaid.initialize({{
  startOnLoad:true, theme:"default",
  state:{{useMaxWidth:false}},
  flowchart:{{useMaxWidth:false}}
}});
</script></body></html>"""

with sync_playwright() as p:
    page = p.chromium.launch(headless=True).new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
    page.set_content(html, wait_until="networkidle")
    page.wait_for_timeout(5000)
    
    svg = page.locator("svg").first
    attrs = page.evaluate("""() => {
        const s = document.querySelector('svg');
        return {
            width: s.getAttribute('width'),
            height: s.getAttribute('height'),
            viewBox: s.getAttribute('viewBox'),
            styleWidth: s.style.width,
            styleHeight: s.style.height,
            innerBBox: s.querySelector('g') ? s.querySelector('g').getBoundingClientRect() : null,
            childCount: s.children.length,
        };
    }""")
    print(f"SVG attrs: {attrs}")
    
    # Try screenshot of the <g> element (the diagram content)
    g = page.locator("svg g").first
    gbox = g.bounding_box()
    print(f"<g> bounding box: {gbox}")
    
    if gbox:
        g.screenshot(path="diagrams/_debug_g.png")
        print("G-element screenshot saved")
    
    browser.close()
