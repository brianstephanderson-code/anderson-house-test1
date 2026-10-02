import base64, json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(".")
OUT = Path("vexy_ichabod_out")
OUT.mkdir(exist_ok=True)
B64 = Path("tomo_bridge/vexy/ichabod_micro.b64")
IMG = OUT / "ichabod_working.jpg"
IMG.write_bytes(base64.b64decode(B64.read_text().strip()))

report={"input":str(IMG),"events":[]}

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={"width":1440,"height":1100},accept_downloads=True)
    page.goto("https://playlines.vexy.art/",wait_until="networkidle",timeout=120000)
    page.screenshot(path=str(OUT/"01_landing.png"),full_page=True)

    fin=page.locator('input[type="file"]')
    if fin.count()<1:
        raise RuntimeError("Vexy file input not found")
    fin.first.set_input_files(str(IMG.resolve()))
    report["events"].append("approved_image_uploaded")
    page.wait_for_timeout(10000)
    page.screenshot(path=str(OUT/"02_vexy_result.png"),full_page=True)

    report["body_text"]=page.locator("body").inner_text()[:12000]
    report["svg_count"]=page.locator("svg").count()
    report["canvas_count"]=page.locator("canvas").count()

    candidates=page.eval_on_selector_all("svg", """els => els.map((e,i)=>{
      const r=e.getBoundingClientRect();
      return {i,area:r.width*r.height,width:r.width,height:r.height,html:e.outerHTML};
    }).sort((a,b)=>b.area-a.area)""")
    report["svg_candidates"]=[{k:v for k,v in c.items() if k!="html"} for c in candidates[:10]]

    if candidates and candidates[0]["area"]>50000:
        svg=candidates[0]["html"]
        (OUT/"ichabod_vexy.svg").write_text(svg,encoding="utf-8")
        report["events"].append("svg_captured")
        report["svg_bytes"]=len(svg.encode("utf-8"))

    # Capture a clean screenshot of the largest artwork SVG when possible.
    if candidates:
        try:
            page.locator("svg").nth(candidates[0]["i"]).screenshot(path=str(OUT/"03_artwork_only.png"))
            report["events"].append("artwork_screenshot_captured")
        except Exception as e:
            report["artwork_screenshot_error"]=str(e)

    (OUT/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
    browser.close()
