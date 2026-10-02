import base64
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

if len(sys.argv) < 3:
    raise SystemExit("usage: run_asset.py INPUT_IMAGE OUTPUT_DIR")

src = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)

if not src.is_file():
    raise SystemExit(f"missing input image: {src}")

report = {
    "function": "three-amigos-vexy-vector-engraving",
    "source": str(src),
    "url": "https://playlines.vexy.art/",
    "events": []
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1100}, accept_downloads=True)
    page.goto(report["url"], wait_until="networkidle", timeout=120000)

    fin = page.locator('input[type="file"]')
    if fin.count() < 1:
        for word in ["Upload", "Drop", "Open", "Image", "Start"]:
            loc = page.get_by_text(word, exact=False)
            if loc.count():
                try:
                    loc.first.click(timeout=2000)
                    page.wait_for_timeout(1000)
                    if page.locator('input[type="file"]').count():
                        break
                except Exception:
                    pass
        fin = page.locator('input[type="file"]')

    if fin.count() < 1:
        raise SystemExit("NO_FILE_INPUT_FOUND")

    fin.first.set_input_files(str(src))
    report["events"].append("image_uploaded")
    page.wait_for_timeout(8000)

    for selector in [
        'text=Linear',
        'button:has-text("Linear")',
        '[role="button"]:has-text("Linear")'
    ]:
        try:
            loc = page.locator(selector)
            if loc.count():
                loc.first.click(timeout=3000)
                report["events"].append("linear_selected")
                page.wait_for_timeout(4000)
                break
        except Exception:
            pass

    page.screenshot(path=str(out / "preview.png"), full_page=True)

    candidates = page.eval_on_selector_all(
        "svg",
        """els => els.map((e,i) => {
            const r=e.getBoundingClientRect();
            return {i, area:r.width*r.height, width:r.width, height:r.height,
                    html:e.outerHTML.slice(0,4000000)};
        }).sort((a,b)=>b.area-a.area)"""
    )

    report["svg_candidates"] = [
        {k:v for k,v in c.items() if k != "html"} for c in candidates[:10]
    ]

    if not candidates or candidates[0]["area"] <= 50000:
        raise SystemExit("NO_LARGE_SVG_CAPTURED")

    best = candidates[0]
    (out / "output.svg").write_text(best["html"], encoding="utf-8")
    report["events"].append("large_svg_captured")

    svg = page.locator("svg").nth(best["i"])
    svg.screenshot(path=str(out / "vexy_result.png"))
    report["events"].append("vexy_result_screenshot")

    im = Image.open(out / "vexy_result.png").convert("RGB")
    im.thumbnail((900, 900), Image.Resampling.LANCZOS)
    preview_path = out / "vexy_result_preview.jpg"
    im.save(preview_path, "JPEG", quality=72, optimize=True, progressive=True)
    b64 = base64.b64encode(preview_path.read_bytes()).decode("ascii")
    (out / "vexy_result_preview.b64").write_text(b64, encoding="ascii")
    chunk_size = 46000
    for n, start in enumerate(range(0, len(b64), chunk_size), 1):
        (out / f"vexy_result_preview.b64.part{n:02d}").write_text(
            b64[start:start+chunk_size], encoding="ascii"
        )
    report["events"].append("portable_preview_created")
    report["preview_b64_length"] = len(b64)
    report["preview_b64_chunks"] = (len(b64) + chunk_size - 1) // chunk_size

    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    browser.close()

print(json.dumps(report, indent=2))
