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
    # Survey the actual effect and tone controls, then cast across every visible engraving effect.
    def largest_svg():
        svs = page.eval_on_selector_all("svg", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,width:r.width,height:r.height,area:r.width*r.height}}).sort((a,b)=>b.area-a.area)""")
        return next((s for s in svs if s["width"] > 0 and s["height"] > 0), None)

    effect_names = ["Line", "Lines", "Line screen", "Wave", "Crosshatch", "Contour", "Isolines", "Spiral", "Rings", "Scribble", "Stipple", "Halftone"]
    report["effect_survey"] = []

    try:
        page.get_by_role("button", name="Effect", exact=True).click()
        page.wait_for_timeout(1200)
        report["effect_panel_text"] = page.locator("body").inner_text()[:12000]
        report["effect_inputs"] = page.eval_on_selector_all("input", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,type:e.type||'',value:e.value||'',min:e.min||'',max:e.max||'',step:e.step||'',checked:!!e.checked,visible:r.width>0&&r.height>0,x:r.x,y:r.y,outerHTML:e.outerHTML.slice(0,1000)}})""")
        report["effect_buttons"] = page.eval_on_selector_all("button", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,text:(e.innerText||'').trim(),visible:r.width>0&&r.height>0,x:r.x,y:r.y,w:r.width,h:r.height,aria:e.getAttribute('aria-label')||'',title:e.title||''}})""")
        (out/"effect_panel.json").write_text(json.dumps({"text":report["effect_panel_text"],"inputs":report["effect_inputs"],"buttons":report["effect_buttons"]},indent=2),encoding="utf-8")

        # Open the effect combobox and enumerate its real options.
        combo = None
        for ii in range(page.locator('button[role="combobox"]').count()):
            loc = page.locator('button[role="combobox"]').nth(ii)
            try:
                box = loc.bounding_box()
                txt = (loc.inner_text() or "").strip()
                if box and box["x"] < 400 and 180 < box["y"] < 300 and txt.lower() != "english":
                    combo = loc
                    break
            except Exception:
                pass

        if combo is None:
            raise RuntimeError("effect combobox not found")

        combo.click()
        page.wait_for_timeout(500)
        option_texts = [t.strip() for t in page.get_by_role("option").all_inner_texts() if t.strip()]
        report["effect_options"] = option_texts
        (out/"effect_options.json").write_text(json.dumps(option_texts,indent=2),encoding="utf-8")
        # Close once before looping.
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)

        for label in option_texts:
            try:
                # Reacquire the combobox each time because its visible text changes.
                combo = None
                for ii in range(page.locator('button[role="combobox"]').count()):
                    loc = page.locator('button[role="combobox"]').nth(ii)
                    box = loc.bounding_box()
                    if box and box["x"] < 400 and 180 < box["y"] < 300:
                        combo = loc
                        break
                if combo is None:
                    raise RuntimeError("effect combobox disappeared")
                combo.click()
                page.wait_for_timeout(250)
                page.get_by_role("option", name=label, exact=True).click()
                page.wait_for_timeout(2500)

                info = largest_svg()
                rec = {"label":label}
                if info and info["area"] > 50000:
                    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in label).strip("_")[:40] or "effect"
                    png = out / ("effect_" + slug + ".png")
                    svg = out / ("effect_" + slug + ".svg")
                    sloc = page.locator("svg").nth(info["i"])
                    if sloc.is_visible():
                        sloc.screenshot(path=str(png), timeout=12000)
                        svg.write_text(sloc.evaluate("e=>e.outerHTML"), encoding="utf-8")
                        rec.update({"captured":True,"png":png.name,"svg":svg.name,"area":info["area"]})
                    else:
                        rec["captured"] = False
                else:
                    rec["captured"] = False
                report["effect_survey"].append(rec)
                (out/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
            except Exception as err:
                report["effect_survey"].append({"label":label,"error":str(err)})
                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass

        report["events"].append("effect_family_survey_complete")
    except Exception as e:
        report["effect_survey_error"] = str(e)

    try:
        page.get_by_role("button", name="Tone", exact=True).click()
        page.wait_for_timeout(900)
        report["tone_panel_text"] = page.locator("body").inner_text()[:12000]
        report["tone_inputs"] = page.eval_on_selector_all("input", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,type:e.type||'',value:e.value||'',min:e.min||'',max:e.max||'',step:e.step||'',checked:!!e.checked,visible:r.width>0&&r.height>0,x:r.x,y:r.y,outerHTML:e.outerHTML.slice(0,1000)}})""")
        report["tone_buttons"] = page.eval_on_selector_all("button", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,text:(e.innerText||'').trim(),visible:r.width>0&&r.height>0,x:r.x,y:r.y,w:r.width,h:r.height,aria:e.getAttribute('aria-label')||'',title:e.title||''}})""")
        report["events"].append("tone_controls_surveyed")
    except Exception as e:
        report["tone_survey_error"] = str(e)

    # Return to Effect for canonical capture after survey.
    try:
        page.get_by_role("button", name="Effect", exact=True).click()
        page.wait_for_timeout(500)
    except Exception:
        pass

    page.screenshot(path=str(out/"page.png"), full_page=True)
    report["events"].append("probe_captured")

    # Persist the survey before any optional canonical capture.
    (out/"report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    canv = [x for x in report["canvases"] if x["cssWidth"]*x["cssHeight"] > 50000]
    try:
        if canv:
            loc = page.locator("canvas").nth(canv[0]["i"])
            if loc.is_visible():
                loc.screenshot(path=str(out/"candidate.png"), timeout=10000)
                report["candidate_type"] = "canvas"
                report["events"].append("candidate_canvas_captured")
        else:
            # Re-evaluate after tab changes and choose only a visible large SVG.
            sv_now = page.eval_on_selector_all("svg", """els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,width:r.width,height:r.height,area:r.width*r.height,visible:!!(r.width&&r.height)}}).filter(x=>x.visible).sort((a,b)=>b.area-a.area)""")
            sv = [x for x in sv_now if x["area"] > 50000]
            if sv:
                loc = page.locator("svg").nth(sv[0]["i"])
                loc.screenshot(path=str(out/"candidate.png"), timeout=10000)
                (out/"candidate.svg").write_text(loc.evaluate("e=>e.outerHTML"), encoding="utf-8")
                report["candidate_type"] = "svg"
                report["events"].append("candidate_svg_captured")
    except Exception as e:
        report["candidate_capture_error"] = str(e)

    (out/"report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    browser.close()

print(json.dumps(report, indent=2))
