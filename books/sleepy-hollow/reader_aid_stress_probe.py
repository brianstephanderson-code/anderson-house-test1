#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pypdf import PdfReader

PROFILES = [
    {"id": "KDP_5X8_STRESS", "width": 5.0, "height": 8.0},
    {"id": "KDP_5_5X8_5_STRESS", "width": 5.5, "height": 8.5},
    {"id": "KDP_6X9_STRESS", "width": 6.0, "height": 9.0},
]
TARGETS = {
    "lexical": 28,
    "named_reference": 55,
    "historical_lexical": 45,
    "cultural_lexical": 65,
}
FILL = "reader aid stress placeholder "

def register_font():
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
    ]:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont("ReaderSerif", path))
            return "ReaderSerif"
    return "Times-Roman"

def extract_body(text):
    start = "*** START OF THE PROJECT GUTENBERG EBOOK THE LEGEND OF SLEEPY HOLLOW ***"
    end = "*** END OF THE PROJECT GUTENBERG EBOOK THE LEGEND OF SLEEPY HOLLOW ***"
    return text.split(start, 1)[1].split(end, 1)[0].strip() + "\n"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")

def placeholder(words, job_id):
    seed = (job_id + " " + FILL).split()
    out = []
    while len(out) < words:
        out.extend(seed)
    return " ".join(out[:words])

def render(body, aids_by_para, profile, out_path, font_name):
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=(profile["width"] * inch, profile["height"] * inch),
        leftMargin=0.5 * inch, rightMargin=0.5 * inch,
        topMargin=0.55 * inch, bottomMargin=0.55 * inch,
        title="Sleepy Hollow Reader Aid Stress Probe",
        author="Washington Irving",
    )
    body_style = ParagraphStyle("Body", fontName=font_name, fontSize=11, leading=14,
                                textColor=black, alignment=TA_LEFT, spaceAfter=8,
                                allowWidows=0, allowOrphans=0)
    title_style = ParagraphStyle("Title", parent=body_style, fontSize=18, leading=22,
                                 alignment=TA_CENTER, spaceAfter=12)
    center_style = ParagraphStyle("Center", parent=body_style, alignment=TA_CENTER, spaceAfter=10)
    aid_style = ParagraphStyle("Aid", fontName=font_name, fontSize=8.5, leading=10.5,
                               textColor=black, alignment=TA_LEFT, leftIndent=10,
                               rightIndent=10, spaceBefore=2, spaceAfter=6)

    story = []
    for i, p in enumerate(paras, start=1):
        style = title_style if i == 1 else center_style if i in (2, 3) else body_style
        story.append(Paragraph(esc(p), style))
        pid = f"P{i:03d}"
        for aid in aids_by_para.get(pid, []):
            label = f'[SYNTHETIC LAYOUT STRESS — {aid["job_id"]}] '
            story.append(Paragraph(esc(label + placeholder(aid["target_words"], aid["job_id"])), aid_style))
        story.append(Spacer(1, 2))

    doc.build(story)
    return len(PdfReader(str(out_path)).pages)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--backlog", required=True)
    ap.add_argument("--assembly-map", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--result", required=True)
    args = ap.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8-sig")
    body = extract_body(raw)
    backlog = json.loads(Path(args.backlog).read_text())
    assembly = json.loads(Path(args.assembly_map).read_text())
    baseline = json.loads(Path(args.baseline).read_text())
    slot_map = {x["job_id"]: x["paragraph_id"] for x in assembly["research_attachment_slots"]}

    aids = []
    for job in backlog["jobs"]:
        job_id = job["job_id"]
        function_class = job["function_class"]
        aids.append({
            "job_id": job_id,
            "paragraph_id": slot_map[job_id],
            "function_class": function_class,
            "target_words": TARGETS.get(function_class, 28),
        })

    aids_by_para = {}
    for aid in aids:
        aids_by_para.setdefault(aid["paragraph_id"], []).append(aid)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    font_name = register_font()
    baseline_by_trim = {tuple(x["trim_inches"]): x["page_count"] for x in baseline["profiles"]}

    rows = []
    for profile in PROFILES:
        pdf_path = out_dir / f'{profile["id"].lower()}.pdf'
        stressed_pages = render(body, aids_by_para, profile, pdf_path, font_name)
        base_pages = baseline_by_trim[(profile["width"], profile["height"])]
        rows.append({
            "profile_id": profile["id"],
            "trim_inches": [profile["width"], profile["height"]],
            "baseline_pages": base_pages,
            "stress_pages": stressed_pages,
            "added_pages": stressed_pages - base_pages,
            "page_growth_percent": round((stressed_pages - base_pages) / base_pages * 100, 1),
            "synthetic_aid_count": len(aids),
            "synthetic_aid_words": sum(x["target_words"] for x in aids),
            "pdf": pdf_path.name,
        })

    result = {
        "work": "The Legend of Sleepy Hollow",
        "probe_id": "SH-READER-AID-STRESS-001",
        "state": "READER_AID_STRESS_MEASURED",
        "source_integrity": {
            "working_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "source_text_changed": False,
        },
        "ownership": {
            "research_jobs_claimed": [],
            "research_job_states_changed": False,
        },
        "stress_model": {
            "synthetic_only": True,
            "purpose": "layout capacity test, not reader-facing content",
            "word_targets_by_function_class": TARGETS,
            "total_aids": len(aids),
            "total_synthetic_words": sum(x["target_words"] for x in aids),
        },
        "profiles": rows,
        "next_state": "COMPARE_TRIM_RESILIENCE_THEN_REPEAT_WITH_REAL_VERIFIED_AIDS",
    }
    Path(args.result).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
