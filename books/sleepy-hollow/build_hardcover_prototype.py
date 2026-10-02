from reportlab.lib.pagesizes import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Flowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pathlib import Path
import json, re, hashlib

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "irving_story_clean.txt"
OUT = ROOT / "build"
OUT.mkdir(exist_ok=True)
PDF = OUT / "sleepy_hollow_hardcover_interior_prototype.pdf"
REPORT = OUT / "build_report.json"

PAGE_W = 5.5*inch
PAGE_H = 8.5*inch
MARGIN_IN = 0.68*inch
MARGIN_OUT = 0.62*inch
MARGIN_TOP = 0.70*inch
MARGIN_BOTTOM = 0.70*inch

styles = getSampleStyleSheet()
body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Times-Roman", fontSize=11.7, leading=17.2, spaceAfter=8, firstLineIndent=0.18*inch)
title = ParagraphStyle("Title", parent=styles["Title"], fontName="Times-Bold", fontSize=21, leading=25, alignment=TA_CENTER, spaceAfter=18)
subtitle = ParagraphStyle("Subtitle", parent=styles["BodyText"], fontName="Times-Italic", fontSize=11, leading=14, alignment=TA_CENTER)
center = ParagraphStyle("Center", parent=styles["BodyText"], fontName="Times-Roman", fontSize=10.5, leading=14, alignment=TA_CENTER)
small = ParagraphStyle("Small", parent=styles["BodyText"], fontName="Times-Roman", fontSize=8.5, leading=11)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Times-Bold", fontSize=13, leading=16, spaceBefore=10, spaceAfter=8)

class Illustration(Flowable):
    def __init__(self, idx, caption):
        super().__init__()
        self.idx=idx; self.caption=caption
        self.width=PAGE_W-1.1*inch
        self.height=PAGE_H-1.6*inch
    def wrap(self, aw, ah):
        return min(self.width,aw), min(self.height,ah)
    def draw(self):
        c=self.canv
        w,h=self.width,self.height
        c.saveState()
        c.setStrokeColor(black); c.setFillColor(white); c.setLineWidth(1.2)
        # frame
        c.rect(0,0,w,h,stroke=1,fill=0)
        # horizon / ground
        c.line(18,h*0.25,w-18,h*0.25)
        # shared moon
        c.circle(w*0.77,h*0.77,22,stroke=1,fill=0)
        # custom motifs
        i=self.idx
        if i==1:
            # valley + distant rider
            c.bezier(10,h*.28,w*.22,h*.46,w*.36,h*.34,w*.50,h*.42)
            c.bezier(w*.45,h*.42,w*.60,h*.55,w*.74,h*.37,w-10,h*.49)
            c.line(w*.18,h*.25,w*.46,h*.08)
            c.circle(w*.63,h*.30,6,stroke=1,fill=0); c.line(w*.63,h*.24,w*.63,h*.12); c.line(w*.58,h*.18,w*.68,h*.18)
        elif i==2:
            # Ichabod silhouette
            c.circle(w*.5,h*.72,18,stroke=1,fill=0)
            c.line(w*.5,h*.69,w*.5,h*.34)
            c.line(w*.5,h*.60,w*.34,h*.43); c.line(w*.5,h*.60,w*.66,h*.43)
            c.line(w*.5,h*.34,w*.38,h*.12); c.line(w*.5,h*.34,w*.62,h*.12)
            c.line(w*.47,h*.76,w*.68,h*.79)
        elif i==3:
            # schoolhouse
            x,y=w*.20,h*.25
            c.rect(x,y,w*.55,h*.30,stroke=1,fill=0)
            c.line(x,y+h*.30,x+w*.275,y+h*.48); c.line(x+w*.275,y+h*.48,x+w*.55,y+h*.30)
            c.rect(x+w*.05,y+h*.08,w*.12,h*.12,stroke=1,fill=0)
            c.rect(x+w*.36,y+h*.05,w*.10,h*.18,stroke=1,fill=0)
            c.line(w*.08,h*.25,w*.13,h*.57); c.line(w*.13,h*.57,w*.16,h*.25)
        elif i==4:
            # reader + dusk trees
            c.circle(w*.34,h*.52,13,stroke=1,fill=0); c.line(w*.34,h*.49,w*.31,h*.30)
            c.line(w*.31,h*.39,w*.47,h*.37); c.line(w*.47,h*.37,w*.52,h*.30)
            c.rect(w*.35,h*.40,w*.12,h*.07,stroke=1,fill=0)
            for x in [w*.68,w*.78,w*.86]:
                c.line(x,h*.25,x,h*.60); c.line(x,h*.56,x-20,h*.43); c.line(x,h*.53,x+18,h*.42)
        elif i==5:
            # farm + Katrina
            c.rect(w*.12,h*.25,w*.45,h*.30,stroke=1,fill=0)
            c.line(w*.12,h*.55,w*.345,h*.70); c.line(w*.345,h*.70,w*.57,h*.55)
            c.circle(w*.75,h*.55,14,stroke=1,fill=0); c.line(w*.75,h*.52,w*.75,h*.30)
            c.line(w*.75,h*.43,w*.66,h*.34); c.line(w*.75,h*.43,w*.84,h*.34)
        elif i==6:
            # horse + rider
            c.ellipse(w*.30,h*.26,w*.67,h*.45,stroke=1,fill=0)
            c.circle(w*.68,h*.40,12,stroke=1,fill=0)
            for xx in [w*.35,w*.58]: c.line(xx,h*.28,xx-12,h*.10)
            c.circle(w*.48,h*.62,12,stroke=1,fill=0); c.line(w*.48,h*.59,w*.50,h*.43)
        elif i==7:
            # feast
            c.rect(w*.13,h*.28,w*.74,h*.12,stroke=1,fill=0)
            for xx in [w*.22,w*.38,w*.54,w*.70]:
                c.ellipse(xx-18,h*.40,xx+18,h*.47,stroke=1,fill=0)
            c.circle(w*.81,h*.50,10,stroke=1,fill=0)
        elif i==8:
            # dance figures
            for xx in [w*.38,w*.60]:
                c.circle(xx,h*.64,12,stroke=1,fill=0); c.line(xx,h*.61,xx,h*.38)
            c.line(w*.38,h*.50,w*.50,h*.44); c.line(w*.60,h*.50,w*.50,h*.44)
            c.line(w*.38,h*.38,w*.28,h*.20); c.line(w*.38,h*.38,w*.47,h*.18)
            c.line(w*.60,h*.38,w*.53,h*.18); c.line(w*.60,h*.38,w*.70,h*.21)
        elif i==9:
            # fireside
            c.rect(w*.15,h*.25,w*.20,h*.28,stroke=1,fill=0)
            c.line(w*.19,h*.25,w*.25,h*.38); c.line(w*.31,h*.25,w*.25,h*.38)
            for xx in [w*.48,w*.62,w*.76]:
                c.circle(xx,h*.50,11,stroke=1,fill=0); c.line(xx,h*.47,xx,h*.31)
        elif i==10:
            # bridge and tree
            c.line(w*.15,h*.24,w*.82,h*.24); c.line(w*.22,h*.30,w*.76,h*.30)
            c.line(w*.68,h*.24,w*.68,h*.68); c.line(w*.68,h*.60,w*.54,h*.46); c.line(w*.68,h*.57,w*.82,h*.43)
            c.bezier(w*.18,h*.18,w*.36,h*.05,w*.50,h*.05,w*.73,h*.17)
        elif i==11:
            # headless rider
            c.ellipse(w*.26,h*.27,w*.68,h*.45,stroke=1,fill=0); c.circle(w*.70,h*.40,11,stroke=1,fill=0)
            c.line(w*.49,h*.44,w*.49,h*.66); c.line(w*.43,h*.60,w*.55,h*.60)
            # carried head
            c.circle(w*.58,h*.50,10,stroke=1,fill=0)
        elif i==12:
            # chase / thrown object
            c.ellipse(w*.18,h*.28,w*.50,h*.42,stroke=1,fill=0); c.ellipse(w*.55,h*.25,w*.85,h*.40,stroke=1,fill=0)
            c.circle(w*.38,h*.57,9,stroke=1,fill=0); c.circle(w*.68,h*.56,9,stroke=1,fill=0)
            c.circle(w*.50,h*.74,8,stroke=1,fill=0); c.line(w*.46,h*.69,w*.42,h*.63); c.line(w*.54,h*.69,w*.58,h*.63)
        # caption
        c.setFont("Times-Italic",9)
        c.drawCentredString(w/2,10,self.caption)
        c.restoreState()

def page_number(canvas, doc):
    n=canvas.getPageNumber()
    canvas.saveState()
    if n>4:
        canvas.setFont("Times-Roman",8)
        canvas.drawCentredString(PAGE_W/2,0.36*inch,str(n))
    canvas.restoreState()

raw=SOURCE.read_text(encoding="utf-8")
sha=hashlib.sha256(raw.encode("utf-8")).hexdigest()
# Remove title/header blocks already handled in front matter.
parts=[p.strip() for p in re.split(r"\n\s*\n",raw) if p.strip()]
body_parts=[]
skip_terms=["THE LEGEND OF SLEEPY HOLLOW","by Washington Irving","FOUND AMONG THE PAPERS"]
for p in parts:
    if any(p.startswith(s) for s in skip_terms):
        continue
    if p.startswith("A pleasing land of drowsy head"):
        continue
    body_parts.append(p)

anchors=[
("From the listless repose",1,"The Hollow"),
("In this by-place of nature",2,"Ichabod Crane"),
("His schoolhouse was",3,"The Schoolhouse"),
("It was often his delight",4,"Reading at Dusk"),
("Among the musical disciples",5,"Katrina and Van Tassel Farm"),
("The most formidable",6,"Brom Bones"),
("Fain would I pause",7,"The Autumn Feast"),
("And now the sound of the music",8,"The Dance"),
("When the dance was at an end",9,"Ghost Stories"),
("As Ichabod approached this fearful tree",10,"The Haunted Bridge"),
("On mounting a rising ground",11,"The Headless Horseman"),
("Just then he heard the black steed",12,"The Chase"),
]
used=set()

story=[]
# Front matter
story += [Spacer(1,1.6*inch), Paragraph("THE LEGEND OF<br/>SLEEPY HOLLOW",title), Paragraph("Washington Irving",subtitle), PageBreak()]
story += [Illustration(1,"Frontispiece: The Hollow"), PageBreak()]
story += [Spacer(1,1.25*inch), Paragraph("The Legend of Sleepy Hollow",title), Paragraph("Washington Irving",subtitle), Spacer(1,0.5*inch), Paragraph("An illustrated Anderson House reader hardcover prototype",center), PageBreak()]
story += [Paragraph("Edition Note",h2), Paragraph("This prototype preserves Washington Irving's public-domain text while adding original Anderson House coded-vector illustrations and production matter. The literary text is kept separate from the production layer.",body), Spacer(1,0.15*inch), Paragraph("<b>Source basis:</b> Project Gutenberg eBook #41 / GITenberg mirror. The original public-domain work is by Washington Irving. Production provenance is maintained separately in the Anderson House repository.",small), PageBreak()]

for p in body_parts:
    inserted=False
    for needle,idx,cap in anchors:
        if idx in used: continue
        if needle.lower() in p.lower():
            if idx!=1:  # frontispiece already used, don't repeat 1
                story += [PageBreak(), Illustration(idx,cap), PageBreak()]
            used.add(idx); inserted=True
            break
    # preserve paragraph text
    text=re.sub(r"\s+"," ",p)
    story.append(Paragraph(text,body))

story += [PageBreak(), Paragraph("Illustrations in This Edition",h2),
          Paragraph("The Hollow; Ichabod Crane; The Schoolhouse; Reading at Dusk; Katrina and the Van Tassel Farm; Brom Bones; The Autumn Feast; The Dance; Ghost Stories; The Haunted Bridge; The Headless Horseman; The Chase.",body),
          PageBreak(),
          Paragraph("Washington Irving",h2),
          Paragraph("Washington Irving (1783-1859) was an American essayist, biographer, historian, and writer of short fiction. <i>The Legend of Sleepy Hollow</i> appeared in <i>The Sketch Book of Geoffrey Crayon, Gent.</i> and combines comic social observation, local legend, and deliberate uncertainty about the supernatural.",body),
          PageBreak(),
          Paragraph("The Setting",h2),
          Paragraph("The story draws on the Hudson River communities around Tarry Town and Sleepy Hollow, using Dutch-settler traditions, Revolutionary-era memories, wooded roads, farms, churchyards, and the river landscape as part of its atmosphere. This edition keeps those setting functions visible in the illustration program without attempting to turn the tale into documentary history.",body),
          PageBreak(),
          Paragraph("About This Edition",h2),
          Paragraph("This is a prototype of a differentiated public-domain hardcover edition. The production system records source provenance, illustration provenance, platform requirements, and verification gates outside the reader-facing text.",body),
          Spacer(1,0.2*inch),
          Paragraph("Production note: the illustrations in this prototype are original vector drawings generated by Anderson House production code and are not copied from third-party artwork.",body),
          PageBreak(),
          Paragraph("Production Provenance",h2),
          Paragraph("Source text: Washington Irving, public-domain work, obtained from the Project Gutenberg / GITenberg source chain. The clean production copy is stored with source lineage in the Anderson House repository. Full internal provenance and verification records are maintained separately so the reading experience remains uncluttered.",body),
          PageBreak()]

doc=SimpleDocTemplate(str(PDF),pagesize=(PAGE_W,PAGE_H),
    rightMargin=MARGIN_OUT,leftMargin=MARGIN_IN,topMargin=MARGIN_TOP,bottomMargin=MARGIN_BOTTOM,
    title="The Legend of Sleepy Hollow",author="Washington Irving")
doc.build(story,onFirstPage=page_number,onLaterPages=page_number)

# count pages with pypdf
from pypdf import PdfReader
reader=PdfReader(str(PDF))
pages=len(reader.pages)
report={
    "file":str(PDF.name),
    "page_count":pages,
    "trim_inches":[5.5,8.5],
    "ink":"black",
    "paper":"cream candidate",
    "interior_bleed":False,
    "source_sha256":sha,
    "illustrations_expected":12,
    "illustration_anchors_found":sorted(list(used)),
    "kdp_hardcover_min_pages":75,
    "meets_minimum":pages>=75,
    "status":"PROTOTYPE_RENDERED"
}
REPORT.write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
