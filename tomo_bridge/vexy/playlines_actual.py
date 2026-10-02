import base64, json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT=Path('vexy_actual_out'); OUT.mkdir(exist_ok=True)
B64=Path('books/sleepy-hollow/art/working/ichabod-vexy-source-600.jpg.b64')
SRC=OUT/'ichabod-vexy-source-600.jpg'
SRC.write_bytes(base64.b64decode(B64.read_text().strip()))
report={'url':'https://playlines.vexy.art/','events':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100})
    page.goto(report['url'],wait_until='networkidle',timeout=120000)
    fin=page.locator('input[type="file"]')
    if fin.count()<1:
        page.screenshot(path=str(OUT/'01_landing.png'),full_page=True)
        report['error']='NO_FILE_INPUT_FOUND'
    else:
        fin.first.set_input_files(str(SRC.resolve()))
        report['events'].append('actual_image_uploaded')
        page.wait_for_timeout(10000)
        page.screenshot(path=str(OUT/'02_after_upload.png'),full_page=True)
        report['svg_count']=page.locator('svg').count()
        candidates=page.eval_on_selector_all('svg',"els=>els.map((e,i)=>{const r=e.getBoundingClientRect();return {i,area:r.width*r.height,width:r.width,height:r.height,html:e.outerHTML.slice(0,4000000)}}).sort((a,b)=>b.area-a.area)")
        report['svg_candidates']=[{k:v for k,v in c.items() if k!='html'} for c in candidates[:10]]
        if candidates and candidates[0]['area']>50000:
            (OUT/'ichabod-vexy-linear.svg').write_text(candidates[0]['html'],encoding='utf-8')
            report['events'].append('actual_svg_captured')
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    browser.close()
print(json.dumps(report,indent=2))
