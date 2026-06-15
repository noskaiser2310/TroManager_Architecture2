"""
Render Mermaid .mmd files to high-quality 2x PNG images using Playwright.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

DIAGRAMS_DIR = Path(__file__).parent


def render_to_png(mmd_path: Path) -> bool:
    definition = mmd_path.read_text(encoding="utf-8")
    out_path = DIAGRAMS_DIR / f"{mmd_path.stem}.png"

    page_content = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
  body {{ margin:0; padding:0; background:white; }}
  svg {{ max-width:none !important; height:auto; display:block; }}
</style>
</head><body>
<pre class="mermaid" id="diagram">{definition}</pre>
<script>
mermaid.initialize({{
  startOnLoad: true,
  theme: "default",
  themeVariables: {{
    fontFamily: "system-ui, -apple-system, sans-serif",
    primaryColor: "#f0f4ff",
    primaryBorderColor: "#3b82f6",
    primaryTextColor: "#1e293b",
    lineColor: "#64748b",
    secondaryColor: "#fef3c7",
    tertiaryColor: "#ecfdf5",
    fontSize: "14px"
  }},
  flowchart:  {{ useMaxWidth:false, htmlLabels:true, curve:"basis", padding:20 }},
  sequence:   {{ useMaxWidth:false, showSequenceNumbers:true, actorFontSize:14, noteFontSize:12 }},
  er:         {{ useMaxWidth:false, layoutDirection:"TB", fontSize:13 }}
}});
</script>
</body></html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
        )
        page = ctx.new_page()
        page.set_content(page_content, wait_until="networkidle")
        page.wait_for_timeout(3000)

        svg_el = page.locator("svg").first
        if svg_el.count() == 0:
            print(f"  FAIL  {mmd_path.name}  no SVG", file=sys.stderr)
            browser.close()
            return False

        # Get the viewBox to know the actual diagram dimensions
        vb = page.evaluate("""() => {
            const s = document.querySelector('svg');
            return s ? s.getAttribute('viewBox') : null;
        }""")

        if vb:
            parts = vb.split()
            pad = 40
            svg_w = int(float(parts[2])) + pad
            svg_h = int(float(parts[3])) + pad
            # Set viewport to match diagram size (at 2x scale factor this works well)
            page.set_viewport_size({"width": svg_w, "height": svg_h})
            page.wait_for_timeout(500)

        page.screenshot(path=str(out_path))
        print(f"  OK    {mmd_path.stem:30s}   viewBox={vb or 'N/A'}   {Path(out_path).stat().st_size//1024}KB")
        browser.close()
    return True


def main():
    mmd_files = sorted(DIAGRAMS_DIR.glob("*.mmd"))
    if not mmd_files:
        print("No .mmd files found")
        return
    print(f"Rendering {len(mmd_files)} diagrams …")
    ok = sum(render_to_png(p) for p in mmd_files)
    print(f"Done: {ok}/{len(mmd_files)} succeeded")


if __name__ == "__main__":
    main()
