import base64
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat
from playwright.sync_api import sync_playwright

if len(sys.argv) < 3:
    raise SystemExit("usage: run_asset.py INPUT_IMAGE OUTPUT_DIR")

src = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)

if not src.is_file():
    raise SystemExit(f"missing input image: {src}")

source_img = Image.open(src).convert("L")
source_thumb = ImageOps.fit(source_img, (512, 384))

report = {
    "function": "three-amigos-vexy-vector-engraving",
    "source": str(src),
    "url": "https://playlines.vexy.art/",
    "events": [],
    "attempts": []
}

def structural_score(candidate_path: Path) -> float:
    try:
        im = Image.open(candidate_path).convert("L")
        im = ImageOps.fit(im, (512, 384))
        # edge-like comparison using autocontrast + difference.
        a = ImageOps.autocontrast(source_thumb)
        b = ImageOps.autocontrast(im)
        diff = ImageChops.difference(a, b)
        mean = ImageStat.Stat(diff).mean[0]
        # lower diff is better; map to 0..1
        return max(0.0, min(1.0, 1.0 - mean / 255.0))
    except Exception:
        return 0.0

def click_text_if_present(page, labels):
    for label in labels:
        for selector in [
            f'text={label}',
            f'button:has-text("{label}")',
            f'[role="button"]:has-text("{label}")'
        ]:
            try:
                loc = page.locator(selector)
                if loc.count():
                    loc.first.click(timeout=2500)
                    page.wait_for_timeout(1200)
                    return True
            except Exception:
                pass
    return False

def capture_largest_svg(page, stem: str):
    candidates = page.eval_on_selector_all(
        "svg",
        """els => els.map((e,i) => {
            const r=e.getBoundingClientRect();
            return {i, area:r.width*r.height, width:r.width, height:r.height,
                    html:e.outerHTML.slice(0,4000000)};
        }).sort((a,b)=>b.area-a.area)"""
    )
    if not candidates or candidates[0]["area"] <= 50000:
        return None
    best = candidates[0]
    svg = page.locator("svg").nth(best["i"])
    png_path = out / f"{stem}.png"
    svg.screenshot(path=str(png_path))
    svg_path = out / f"{stem}.svg"
    svg_path.write_text(best["html"], encoding="utf-8")
    return {
        "png": png_path,
        "svg": svg_path,
        "candidate": {k:v for k,v in best.items() if k != "html"}
    }

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1100}, accept_downloads=True)
    page.goto(report["url"], wait_until="networkidle", timeout=120000)

    fin = page.locator('input[type="file"]')
    if fin.count() < 1:
        click_text_if_present(page, ["Upload", "Drop", "Open", "Image", "Start"])
        fin = page.locator('input[type="file"]')
    if fin.count() < 1:
        raise SystemExit("NO_FILE_INPUT_FOUND")

    fin.first.set_input_files(str(src))
    report["events"].append("image_uploaded")
    page.wait_for_timeout(7000)

    # Save post-upload UI evidence.
    page.screenshot(path=str(out / "after_upload.png"), full_page=True)

    # Explicitly try free fill modes, starting with Linear.
    fill_labels = ["Linear", "Dots", "Stipple", "ASCII", "Wireframe"]
    best_attempt = None

    for idx, fill in enumerate(fill_labels, start=1):
        selected = click_text_if_present(page, [fill])
        page.wait_for_timeout(2500)

        # Try modest generic steering on visible range inputs.
        sliders = page.locator('input[type="range"]')
        slider_count = sliders.count()
        changed = []
        if slider_count:
            # explore a few deterministic states; browser will ignore unsupported values.
            positions = [0.25, 0.5, 0.75]
            pos = positions[(idx - 1) % len(positions)]
            for sidx in range(min(slider_count, 4)):
                try:
                    s = sliders.nth(sidx)
                    meta = s.evaluate("""e => ({
                        min: parseFloat(e.min || 0),
                        max: parseFloat(e.max || 100),
                        step: parseFloat(e.step || 1),
                        value: parseFloat(e.value || 0)
                    })""")
                    lo, hi = meta["min"], meta["max"]
                    val = lo + (hi - lo) * pos
                    s.evaluate("(e,v) => { e.value=v; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); }", val)
                    changed.append({"index": sidx, "value": val})
                    page.wait_for_timeout(350)
                except Exception:
                    pass

        page.wait_for_timeout(2500)
        shot = capture_largest_svg(page, f"attempt_{idx}_{fill.lower()}")
        if not shot:
            report["attempts"].append({"fill":fill,"selected":selected,"sliders_changed":changed,"score":0.0,"captured":False})
            continue

        score = structural_score(shot["png"])
        attempt = {
            "fill": fill,
            "selected": selected,
            "sliders_changed": changed,
            "score": score,
            "captured": True,
            "svg_candidate": shot["candidate"],
            "png": shot["png"].name,
            "svg": shot["svg"].name
        }
        report["attempts"].append(attempt)
        if best_attempt is None or score > best_attempt["score"]:
            best_attempt = attempt

    if not best_attempt:
        raise SystemExit("NO_VEXY_ATTEMPT_CAPTURED")

    # Promote best evidence to canonical output.
    best_png = out / best_attempt["png"]
    best_svg = out / best_attempt["svg"]
    (out / "output.svg").write_text(best_svg.read_text(encoding="utf-8"), encoding="utf-8")
    Image.open(best_png).save(out / "vexy_result.png")

    im = Image.open(best_png).convert("RGB")
    im.thumbnail((900, 900), Image.Resampling.LANCZOS)
    preview_path = out / "vexy_result_preview.jpg"
    im.save(preview_path, "JPEG", quality=76, optimize=True, progressive=True)
    (out / "vexy_result_preview.b64").write_text(
        base64.b64encode(preview_path.read_bytes()).decode("ascii"),
        encoding="ascii"
    )

    report["best_attempt"] = best_attempt
    report["events"].append("steer_inspect_loop_complete")
    report["events"].append("portable_preview_created")
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    browser.close()

print(json.dumps(report, indent=2))
