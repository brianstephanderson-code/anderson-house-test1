import json, os, time
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

OUT = Path("vexy_probe_out")
OUT.mkdir(exist_ok=True)

# Production input if present; otherwise retain the synthetic probe fallback.
INPUT = Path(os.environ.get(
    "VEXY_INPUT",
    "tomo_bridge/vexy/input/ichabod_vexy_input.jpg"
))
if INPUT.exists():
    SRC = INPUT
    source_mode = "production_input"
else:
    SRC = OUT / "probe_input.png"
    source_mode = "synthetic_probe"
    im = Image.new("L", (640, 480), 245)
    d = ImageDraw.Draw(im)
    d.ellipse((70, 70, 300, 360), fill=70)
    d.rectangle((340, 90, 570, 360), fill=140)
    d.line((0, 450, 640, 30), fill=15, width=24)
    d.text((24, 18), "VEXY PROBE", fill=0)
    im.save(SRC)

report = {
    "url": "https://playlines.vexy.art/",
    "events": [],
    "source_mode": source_mode,
    "source_path": str(SRC)
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1100}, accept_downloads=True)

    page.goto(report["url"], wait_until="networkidle", timeout=120000)
    page.screenshot(path=str(OUT / "01_landing.png"), full_page=True)

    # Inventory UI before touching it.
    report["title"] = page.title()
    report["inputs"] = page.locator("input").count()
    report["file_inputs"] = page.locator('input[type="file"]').count()
    report["buttons"] = page.locator("button").all_inner_texts()
    report["body_text"] = page.locator("body").inner_text()[:12000]

    fin = page.locator('input[type="file"]')
    if fin.count() < 1:
        # Some drop-zone apps hide/create the input after a click.
        for word in ["Upload", "Drop", "Open", "Image", "Start"]:
            loc = page.get_by_text(word, exact=False)
            if loc.count():
                try:
                    loc.first.click(timeout=2000)
                    time.sleep(1)
                    if page.locator('input[type="file"]').count():
                        break
                except Exception:
                    pass
        fin = page.locator('input[type="file"]')

    if fin.count() < 1:
        report["error"] = "NO_FILE_INPUT_FOUND"
    else:
        fin.first.set_input_files(str(SRC.resolve()))
        report["events"].append("image_uploaded")
        page.wait_for_timeout(8000)
        page.screenshot(path=str(OUT / "02_after_upload.png"), full_page=True)

        # Try to select the free Linear mode if a visible control exists.
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

        page.screenshot(path=str(OUT / "03_after_linear.png"), full_page=True)

        # Save UI inventory after processing.
        report["after_buttons"] = page.locator("button").all_inner_texts()
        report["after_body_text"] = page.locator("body").inner_text()[:16000]
        report["svg_count"] = page.locator("svg").count()
        report["canvas_count"] = page.locator("canvas").count()

        # Choose the largest rendered SVG candidate. If artwork is SVG, this captures it
        # without requiring the site's Download button.
        candidates = page.eval_on_selector_all(
            "svg",
            """els => els.map((e,i) => {
                const r=e.getBoundingClientRect();
                return {i, area:r.width*r.height, width:r.width, height:r.height,
                        html:e.outerHTML.slice(0,2000000)};
            }).sort((a,b)=>b.area-a.area)"""
        )
        report["svg_candidates"] = [
            {k:v for k,v in c.items() if k != "html"} for c in candidates[:10]
        ]
        if candidates and candidates[0]["area"] > 50000:
            (OUT / "candidate.svg").write_text(candidates[0]["html"], encoding="utf-8")
            report["events"].append("large_svg_captured")

        # Also try an actual free Download/Copy SVG control if present.
        dl_words = ["Download SVG", "Download", "SVG"]
        for word in dl_words:
            try:
                loc = page.get_by_text(word, exact=False)
                if loc.count():
                    report.setdefault("download_controls", []).append(
                        {"text": word, "count": loc.count()}
                    )
            except Exception:
                pass

    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    browser.close()

print(json.dumps(report, indent=2))
