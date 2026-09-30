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
    {"id": "KDP_5X8_PROBE", "width": 5.0, "height": 8.0},
    {"id": "KDP_5_5X8_5_PROBE", "width": 5.5, "height": 8.5},
    {"id": "KDP_6X9_PROBE", "width": 6.0, "height": 9.0},
]

def inside_min(page_count):
    if 24 <= page_count <= 150: return 0.375
    if 151 <= page_count <= 300: return 0.5
    if 301 <= page_count <= 500: return 0.625
    if 501 <= page_count <= 700: return 0.75
    if 701 <= page_count <= 828: return 0.875
    return None

def register_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont("ReaderSerif", path))
            return "ReaderSerif"
    return "Times-Roman"

def extract_body(text):
    start = "*** START OF THE PROJECT GUTENBERG EBOOK THE LEGEND OF SLEEPY HOLLOW ***"
    end = "*** END OF THE PROJECT GUTENBERG EBOOK THE LEGEND OF SLEEPY HOLLOW ***"
    if start not in text or end not in text:
        raise SystemExit("Gutenberg story boundaries not found")
    return text.split(start, 1)[1].split(end, 1)[0].strip() + "\n"

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace("\n", "<br/>"))

def render(body, profile, out_path, font_name):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    width = profile["width"] * inch
    height = profile["height"] * inch

    # Probe margins are intentionally conservative and symmetric.
    # Final mirrored margins are selected only after page count is known.
    margin = 0.5 * inch

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=(width, height),
        leftMargin=margin,
        rightMargin=margin,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="The Legend of Sleepy Hollow — Reader Edition pagination probe",
        author="Washington Irving",
    )

    body_style = ParagraphStyle(
        "Body",
        fontName=font_name,
        fontSize=11,
        leading=14,
        textColor=black,
        alignment=TA_LEFT,
        spaceAfter=8,
        allowWidows=0,
        allowOrphans=0,
    )
    title_style = ParagraphStyle(
        "Title",
        parent=body_style,
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    center_style = ParagraphStyle(
        "Center",
        parent=body_style,
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    story = []
    for i, p in enumerate(paragraphs):
        if i == 0:
            style = title_style
        elif i in (1, 2):
            style = center_style
        else:
            style = body_style
        story.append(Paragraph(esc(p), style))
        story.append(Spacer(1, 2))

    doc.build(story)
    return len(PdfReader(str(out_path)).pages)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--result", required=True)
    args = ap.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8-sig")
    body = extract_body(raw)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    font_name = register_font()

    source_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    word_count = len(re.findall(r"\S+", body))
    paragraph_count = len([p for p in re.split(r"\n\s*\n", body) if p.strip()])

    rows = []
    for profile in PROFILES:
        pdf_path = out_dir / f'{profile["id"].lower()}.pdf'
        pages = render(body, profile, pdf_path, font_name)
        minimum_inside = inside_min(pages)
        rows.append({
            "profile_id": profile["id"],
            "trim_inches": [profile["width"], profile["height"]],
            "font": font_name,
            "font_size_pt": 11,
            "leading_pt": 14,
            "probe_margins_inches": {
                "inside": 0.5,
                "outside": 0.5,
                "top": 0.55,
                "bottom": 0.55
            },
            "page_count": pages,
            "kdp_inside_margin_min_inches_for_observed_page_count": minimum_inside,
            "probe_inside_margin_meets_current_kdp_minimum": (
                minimum_inside is not None and 0.5 >= minimum_inside
            ),
            "pdf": pdf_path.name
        })

    result = {
        "work": "The Legend of Sleepy Hollow",
        "probe_id": "SH-PAGINATION-PROBE-001",
        "state": "PAGINATION_MEASURED",
        "source": {
            "provider": "Project Gutenberg",
            "ebook_id": 41,
            "working_body_sha256": source_sha,
            "word_count": word_count,
            "paragraph_count": paragraph_count
        },
        "method": {
            "renderer": "ReportLab",
            "purpose": "measure real PDF pagination under three candidate KDP trim profiles without choosing a final trim",
            "bleed": False,
            "reader_aids_inserted": False,
            "note": "These are measured prototype page counts, not final publication page counts. Reader aids and later typographic refinements can change pagination."
        },
        "profiles": rows,
        "next_state": "USE_MEASURED_PAGE_COUNT_TO_SELECT_OR_RECAST_PRINT_PROFILE"
    }
    Path(args.result).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
