import base64, json, sys
from pathlib import Path
from PIL import Image, ImageOps, ImageChops, ImageStat
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

    report["file_input_inventory"] = page.eval_on_selector_all(
        'input[type="file"]',
        """els => els.map((e,i) => {
            const r=e.getBoundingClientRect();
            return {i, accept:e.accept||'', name:e.name||'', id:e.id||'',
                    className:String(e.className||''), width:r.width, height:r.height,
                    x:r.x, y:r.y, outerHTML:e.outerHTML.slice(0,1200)};
        })"""
    )
    report["button_inventory"] = page.eval_on_selector_all(
        "button",
        """els => els.map((e,i) => {
            const r=e.getBoundingClientRect();
            return {i, text:(e.innerText||'').trim(), aria:e.getAttribute('aria-label')||'',
                    title:e.getAttribute('title')||'', width:r.width, height:r.height,
                    x:r.x, y:r.y, outerHTML:e.outerHTML.slice(0,1200)};
        })"""
    )
    (out / "dom_inventory.json").write_text(json.dumps({
        "file_inputs": report["file_input_inventory"],
        "buttons": report["button_inventory"]
    }, indent=2), encoding="utf-8")

    uploaded = False

    # First try an input explicitly accepting images.
    inputs = page.locator('input[type="file"]')
    for i in range(inputs.count()):
        try:
            accept = (inputs.nth(i).get_attribute("accept") or "").lower()
            if "image" in accept or any(x in accept for x in [".png", ".jpg", ".jpeg", ".webp"]):
                inputs.nth(i).set_input_files(str(src))
                uploaded = True
                report["events"].append(f"image_uploaded_via_input_{i}")
                break
        except Exception as e:
            report.setdefault("input_errors", []).append({"i": i, "error": str(e)})

    # Then try the visible Choose image control.
    if not uploaded:
        try:
            choose = page.get_by_text("Choose image", exact=False)
            if choose.count():
                with page.expect_file_chooser(timeout=3500) as fc:
                    choose.first.click()
                fc.value.set_files(str(src))
                uploaded = True
                report["events"].append("image_uploaded_via_choose_image")
        except Exception as e:
            report["choose_image_error"] = str(e)

    # Finally probe small buttons in the left image strip, including the +.
    if not uploaded:
        btns = page.locator("button")
        candidates = [
            b for b in report["button_inventory"]
            if b["width"] <= 70 and b["height"] <= 70 and b["x"] < 160 and b["y"] < 460
        ]
        report["sidebar_button_candidates"] = candidates
        for b in candidates:
            try:
                with page.expect_file_chooser(timeout=2500) as fc:
                    btns.nth(b["i"]).click()
                fc.value.set_files(str(src))
                uploaded = True
                report["events"].append(f"image_uploaded_via_sidebar_button_{b['i']}")
                break
            except Exception:
                pass

    if not uploaded:
        report["error"] = "NO_IMAGE_UPLOAD_CONTROL_FOUND"
        (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        page.screenshot(path=str(out / "upload_failure.png"), full_page=True)
        browser.close()
        raise SystemExit("NO_IMAGE_UPLOAD_CONTROL_FOUND")

    page.wait_for_timeout(5000)
    report["after_file_inputs"] = page.eval_on_selector_all(
        'input[type="file"]',
        """els => els.map((e,i) => ({i,accept:e.accept||'',value:e.value||'',outerHTML:e.outerHTML.slice(0,800)}))"""
    )
    report["image_inventory"] = page.eval_on_selector_all(
        "img",
        """els => els.map((e,i) => {
            const r=e.getBoundingClientRect();
            return {i, naturalWidth:e.naturalWidth, naturalHeight:e.naturalHeight,
                    width:r.width, height:r.height, x:r.x, y:r.y,
                    src:(e.src||'').slice(0,200), alt:e.alt||''};
        })"""
    )

    # Prefer a newly-added image tile matching source aspect ratio and click it.
    src_im = Image.open(src)
    src_w, src_h = src_im.size
    src_im.close()
    target_ratio = src_w / max(src_h, 1)
    custom = []
    for info in report["image_inventory"]:
        nw, nh = info["naturalWidth"], info["naturalHeight"]
        if nw <= 0 or nh <= 0:
            continue
        ratio_err = abs((nw / nh) - target_ratio)
        # Custom uploads often become blob/data URLs. Prefer those.
        bonus = -10 if info["src"].startswith(("blob:", "data:")) else 0
        if nw == src_w and nh == src_h:
            bonus -= 20
        custom.append((ratio_err + bonus, info["i"], info))
    custom.sort(key=lambda x: x[0])
    report["image_rank"] = [x[2] for x in custom[:8]]
    if custom:
        try:
            page.locator("img").nth(custom[0][1]).click(timeout=5000)
            report["events"].append(f"image_selected_{custom[0][1]}")
            page.wait_for_timeout(12000)
        except Exception as e:
            report["image_select_error"] = str(e)

    # Prove the uploaded source is actually bound to Playlines.
    try:
        stage = page.locator("#stageImg")
        if stage.count():
            src_meta = stage.evaluate("""e => ({
                src:(e.src||'').slice(0,120),
                naturalWidth:e.naturalWidth,
                naturalHeight:e.naturalHeight
            })""")
            report["source_binding"] = src_meta
            report["source_bound"] = bool(src_meta["naturalWidth"] and src_meta["naturalHeight"] and src_meta["src"].startswith("data:image"))
            if report["source_bound"]:
                report["events"].append("source_binding_verified")
    except Exception as e:
        report["source_binding_error"] = str(e)

    # Save the exact image Playlines bound to #stageImg and compare it with
    # the repository source. This distinguishes a real source load from the
    # built-in demo image.
    try:
        import io
        stage = page.locator("#stageImg")
        stage_src = stage.get_attribute("src") if stage.count() else ""
        if stage_src and stage_src.startswith("data:image") and "," in stage_src:
            raw = base64.b64decode(stage_src.split(",",1)[1])
            (out / "stage_source.png").write_bytes(raw)
            stage_im = Image.open(io.BytesIO(raw)).convert("RGB")
            stage_preview = stage_im.copy()
            stage_preview.thumbnail((900,900), Image.Resampling.LANCZOS)
            stage_preview_path = out / "stage_source_preview.jpg"
            stage_preview.save(stage_preview_path, "JPEG", quality=80, optimize=True)
            (out / "stage_source_preview.b64").write_text(
                base64.b64encode(stage_preview_path.read_bytes()).decode("ascii"),
                encoding="ascii"
            )
            ref_im = Image.open(src).convert("RGB").resize(stage_im.size, Image.Resampling.LANCZOS)
            stage_gray = ImageOps.autocontrast(stage_im.convert("L"))
            ref_gray = ImageOps.autocontrast(ref_im.convert("L"))
            diff = ImageChops.difference(stage_gray, ref_gray)
            mad = ImageStat.Stat(diff).mean[0]
            report["source_binding_mad"] = mad
            report["source_binding_matches_input"] = mad < 35
            report["stage_source_size"] = list(stage_im.size)
            report["events"].append("stage_source_saved")
    except Exception as e:
        report["stage_source_extract_error"] = str(e)

    # Capture the source view as evidence before transforming.
    try:
        page.locator("#viewSource").click(force=True, timeout=3000)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(out / "source_view.png"), full_page=True)
        report["events"].append("source_view_captured")
        page.locator("#viewResult").click(force=True, timeout=3000)
        page.wait_for_timeout(1200)
    except Exception as e:
        report["source_view_error"] = str(e)

    # Select the actual visible Linear button. Earlier generic text selectors
    # were hitting hidden duplicate controls, leaving Playlines in Wave mode.
    try:
        linear = page.locator("#fillLinear")
        if not linear.count():
            linear = page.locator('button.fillBtn[title="Linear"]:visible')
        linear.first.click(force=True, timeout=5000)
        page.wait_for_timeout(6000)
        report["events"].append("linear_selected_visible_control")
        try:
            report["active_fill_label"] = page.locator("#fillLabel").inner_text(timeout=2000)
        except Exception:
            pass
    except Exception as e:
        report["linear_select_error"] = str(e)

    # Inventory live tuning sliders so the next pass can steer deliberately.
    report["range_inventory"] = page.eval_on_selector_all(
        'input[type="range"]',
        """els => els.map((e,i) => ({
            i, id:e.id||'', min:e.min||'', max:e.max||'', step:e.step||'',
            value:e.value||'', name:e.name||'', title:e.title||'',
            aria:e.getAttribute('aria-label')||''
        }))"""
    )


    # Compare the free Playlines fill families against the same verified source.
    # Linear has been proven source-bound but visually unsuitable, so cast wider.
    def set_range(id_, value):
        loc = page.locator("#" + id_)
        if not loc.count():
            return False
        loc.evaluate(
            """(e,v) => {
                e.value = String(v);
                e.dispatchEvent(new Event('input',{bubbles:true}));
                e.dispatchEvent(new Event('change',{bubbles:true}));
            }""",
            value,
        )
        return True

    source_for_score = Image.open(src).convert("L")
    source_for_score = ImageOps.fit(source_for_score, (512,384))
    source_for_score = ImageOps.autocontrast(source_for_score)

    def score_png(path):
        try:
            cand = Image.open(path).convert("L")
            cand = ImageOps.fit(cand, (512,384))
            cand = ImageOps.autocontrast(cand)
            diff = ImageChops.difference(source_for_score, cand)
            return max(0.0, min(1.0, 1.0 - ImageStat.Stat(diff).mean[0] / 255.0))
        except Exception:
            return 0.0

    fill_tests = [
        {"id":"fillLinear",   "name":"Linear",   "params":{"thickness":35,"interval":70,"organic":10,"contrast":1.0,"brightness":55}},
        {"id":"fillWave",     "name":"Wave",     "params":{"thickness":120,"interval":220,"organic":20,"contrast":1.25,"brightness":0}},
        {"id":"fillCircular", "name":"Circular", "params":{"thickness":120,"interval":220,"organic":20,"contrast":1.25,"brightness":0}},
        {"id":"fillSpiral",   "name":"Spiral",   "params":{"thickness":120,"interval":220,"organic":20,"contrast":1.25,"brightness":0}},
        {"id":"fillHalftone", "name":"Halftone", "params":{"thickness":120,"interval":220,"organic":0,"contrast":1.35,"brightness":0}},
    ]

    report["fill_family_tests"] = []
    best_fill = None

    for idx, test in enumerate(fill_tests, start=1):
        try:
            btn = page.locator("#" + test["id"])
            btn.click(force=True, timeout=5000)
            page.wait_for_timeout(3500)
        except Exception as e:
            report["fill_family_tests"].append({"name":test["name"],"selected":False,"error":str(e),"score":0.0})
            continue

        for key, val in test["params"].items():
            set_range(key, val)
        page.wait_for_timeout(3000)

        label = None
        try:
            label = page.locator("#fillLabel").inner_text(timeout=1500)
        except Exception:
            pass

        candidates_now = page.eval_on_selector_all(
            "svg",
            """els => els.map((e,i) => {
                const r=e.getBoundingClientRect();
                return {i, area:r.width*r.height, width:r.width, height:r.height};
            }).sort((a,b)=>b.area-a.area)"""
        )
        if not candidates_now or candidates_now[0]["area"] <= 50000:
            report["fill_family_tests"].append({"name":test["name"],"selected":True,"active_label":label,"score":0.0,"captured":False})
            continue

        svgi = candidates_now[0]["i"]
        png_path = out / f"fill_{idx}_{test['name'].lower()}.png"
        svg_path = out / f"fill_{idx}_{test['name'].lower()}.svg"
        page.locator("svg").nth(svgi).screenshot(path=str(png_path))
        html = page.locator("svg").nth(svgi).evaluate("e => e.outerHTML")
        svg_path.write_text(html,encoding="utf-8")
        sc = score_png(png_path)
        rec={"name":test["name"],"selected":True,"active_label":label,"score":sc,
             "png":png_path.name,"svg":svg_path.name,"params":test["params"]}
        report["fill_family_tests"].append(rec)
        if best_fill is None or sc > best_fill["score"]:
            best_fill=rec

    if best_fill:
        report["best_fill"] = best_fill
        report["events"].append("free_fill_family_survey_complete")
        # restore best fill/parameters before canonical export
        best_id = next(x["id"] for x in fill_tests if x["name"]==best_fill["name"])
        page.locator("#"+best_id).click(force=True, timeout=5000)
        for key,val in best_fill["params"].items():
            set_range(key,val)
        page.wait_for_timeout(3500)
    page.screenshot(path=str(out / "preview.png"), full_page=True)
    candidates = page.eval_on_selector_all(
        "svg",
        """els => els.map((e,i) => {
            const r=e.getBoundingClientRect();
            return {i, area:r.width*r.height, width:r.width, height:r.height,
                    html:e.outerHTML.slice(0,4000000)};
        }).sort((a,b)=>b.area-a.area)"""
    )
    report["svg_candidates"] = [{k:v for k,v in c.items() if k!="html"} for c in candidates[:10]]
    if not candidates or candidates[0]["area"] <= 50000:
        report["error"] = "NO_LARGE_SVG_CAPTURED"
        (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        browser.close()
        raise SystemExit("NO_LARGE_SVG_CAPTURED")

    best = candidates[0]
    (out / "output.svg").write_text(best["html"], encoding="utf-8")
    svg = page.locator("svg").nth(best["i"])
    svg.screenshot(path=str(out / "vexy_result.png"))
    report["events"].append("large_svg_captured")

    im = Image.open(out / "vexy_result.png").convert("RGB")
    im.thumbnail((900, 900), Image.Resampling.LANCZOS)
    preview_path = out / "vexy_result_preview.jpg"
    im.save(preview_path, "JPEG", quality=72, optimize=True, progressive=True)
    b64 = base64.b64encode(preview_path.read_bytes()).decode("ascii")
    (out / "vexy_result_preview.b64").write_text(b64, encoding="ascii")
    report["events"].append("portable_preview_created")
    report["preview_b64_length"] = len(b64)
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    browser.close()

print(json.dumps(report, indent=2))
