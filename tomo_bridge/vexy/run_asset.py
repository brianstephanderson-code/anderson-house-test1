import base64, json, sys
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

    # If Linear is exposed, select it.
    for selector in ['text=Linear','button:has-text("Linear")','[role="button"]:has-text("Linear")']:
        try:
            loc = page.locator(selector)
            if loc.count():
                loc.first.click(timeout=3000)
                report["events"].append("linear_selected")
                page.wait_for_timeout(5000)
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
