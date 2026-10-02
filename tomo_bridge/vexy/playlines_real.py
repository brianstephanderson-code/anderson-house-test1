import base64, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("vexy_real_out")
OUT.mkdir(exist_ok=True)
SRC = OUT / "ichabod_vexy_input.jpg"

b64_path = Path("tomo_bridge/vexy/input/ichabod_vexy_probe.jpg.b64")
SRC.write_bytes(base64.b64decode(b64_path.read_text().strip()))

report = {"url":"https://playlines.vexy.art/","events":[],"source":"approved_ichabod_horseman_processing_copy"}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width":1440,"height":1100}, accept_downloads=True)
    page.goto(report["url"], wait_until="networkidle", timeout=120000)
    page.screenshot(path=str(OUT/"01_landing.png"), full_page=True)

    fin = page.locator('input[type="file"]')
    if fin.count() < 1:
        report["error"]="NO_FILE_INPUT_FOUND"
    else:
        fin.first.set_input_files(str(SRC.resolve()))
        report["events"].append("real_image_uploaded")
        page.wait_for_timeout(10000)
        page.screenshot(path=str(OUT/"02_real_after_upload.png"), full_page=True)

        # Vexy currently opens in Linear by default; still record any visible Linear control.
        linear = page.get_by_text("Linear", exact=False)
        report["linear_controls"]=linear.count()
        report["body_text"]=page.locator("body").inner_text()[:16000]
        report["svg_count"]=page.locator("svg").count()
        report["canvas_count"]=page.locator("canvas").count()

        candidates = page.eval_on_selector_all(
            "svg",
            """els => els.map((e,i)=>{const r=e.getBoundingClientRect();
            return {i,area:r.width*r.height,width:r.width,height:r.height,
            html:e.outerHTML.slice(0,4000000)};}).sort((a,b)=>b.area-a.area)"""
        )
        report["svg_candidates"]=[{k:v for k,v in c.items() if k!="html"} for c in candidates[:10]]
        if candidates and candidates[0]["area"] > 50000:
            (OUT/"ichabod_vexy_candidate.svg").write_text(candidates[0]["html"],encoding="utf-8")
            report["events"].append("real_svg_captured")

        # Capture the processed artwork area as rendered by Vexy for Linda.
        page.screenshot(path=str(OUT/"03_real_final.png"), full_page=True)

    (OUT/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    browser.close()

print(json.dumps(report,indent=2))
