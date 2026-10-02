import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if len(sys.argv) < 3:
    raise SystemExit("usage: run_asset.py INPUT_IMAGE OUTPUT_DIR")

src = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
if not src.is_file():
    raise SystemExit("missing input image: " + str(src))

report = {"function":"three-amigos-boxlab-engraver","source":str(src),"url":"https://boxlab.io/tools/engraver/app/en","events":[]}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width":1440,"height":1100}, accept_downloads=True)
    page.goto(report["url"], wait_until="networkidle", timeout=120000)

    report["inputs"] = page.eval_on_selector_all("input", """els=>els.map((e,i)=>({i,type:e.type||'',id:e.id||'',name:e.name||'',accept:e.accept||'',value:e.value||'',min:e.min||'',max:e.max||'',step:e.step||'',aria:e.getAttribute('aria-label')||'',title:e.title||'',outerHTML:e.outerHTML.slice(0,1200)}))""")
    report["buttons"] = page.eval_on_selector_all("button", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,text:(e.innerText||'').trim(),id:e.id||'',aria:e.getAttribute('aria-label')||'',title:e.title||'',width:r.width,height:r.height,x:r.x,y:r.y,outerHTML:e.outerHTML.slice(0,1200)}})""")
    report["selects"] = page.eval_on_selector_all("select", """els=>els.map((e,i)=>({i,id:e.id||'',name:e.name||'',value:e.value||'',outerHTML:e.outerHTML.slice(0,1600)}))""")
    (out/"dom_inventory.json").write_text(json.dumps({"inputs":report["inputs"],"buttons":report["buttons"],"selects":report["selects"]}, indent=2), encoding="utf-8")

    uploaded = False
    files = page.locator('input[type="file"]')
    for i in range(files.count()):
        try:
            files.nth(i).set_input_files(str(src))
            uploaded = True
            report["events"].append("image_uploaded_via_input_" + str(i))
            break
        except Exception as e:
            report.setdefault("upload_errors", []).append(str(e))

    if not uploaded:
        for b in report["buttons"]:
            s = (b["text"]+" "+b["aria"]+" "+b["title"]).lower()
            if any(k in s for k in ["upload","choose image","open image","engrave a picture","choose file"]):
                try:
                    with page.expect_file_chooser(timeout=3500) as fc:
                        page.locator("button").nth(b["i"]).click()
                    fc.value.set_files(str(src))
                    uploaded = True
                    report["events"].append("image_uploaded_via_button_" + str(b["i"]))
                    break
                except Exception:
                    pass

    page.wait_for_timeout(7000)
    report["uploaded"] = uploaded
    report["after_inputs"] = page.eval_on_selector_all("input", """els=>els.map((e,i)=>({i,type:e.type||'',id:e.id||'',value:e.value||'',checked:!!e.checked,min:e.min||'',max:e.max||'',step:e.step||'',aria:e.getAttribute('aria-label')||'',title:e.title||''}))""")
    report["canvases"] = page.eval_on_selector_all("canvas", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,width:e.width,height:e.height,cssWidth:r.width,cssHeight:r.height,x:r.x,y:r.y}})""")
    report["svgs"] = page.eval_on_selector_all("svg", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,width:r.width,height:r.height,area:r.width*r.height}}).sort((a,b)=>b.area-a.area)""")
    page.screenshot(path=str(out/"page.png"), full_page=True)
    report["events"].append("probe_captured")

    canv = [x for x in report["canvases"] if x["cssWidth"]*x["cssHeight"] > 50000]
    if canv:
        page.locator("canvas").nth(canv[0]["i"]).screenshot(path=str(out/"candidate.png"))
        report["candidate_type"] = "canvas"
        report["events"].append("candidate_canvas_captured")
    else:
        sv = [x for x in report["svgs"] if x["area"] > 50000]
        if sv:
            loc = page.locator("svg").nth(sv[0]["i"])
            loc.screenshot(path=str(out/"candidate.png"))
            (out/"candidate.svg").write_text(loc.evaluate("e=>e.outerHTML"), encoding="utf-8")
            report["candidate_type"] = "svg"
            report["events"].append("candidate_svg_captured")

    (out/"report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    browser.close()

print(json.dumps(report, indent=2))
