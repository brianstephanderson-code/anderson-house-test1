# Sleepy Hollow — Bill / Ted / Linda Hardcover Bridge 001

## Job
**Purpose:** Produce one standard Amazon KDP hardcover edition of *The Legend of Sleepy Hollow* before branching into other product forms.

**START STATE:** Existing Anderson House Sleepy Hollow source gate, working-copy structure, print experiments, warehouse functions, research functions, and current external resources.

**TARGET DONE:** A verified KDP-upload-ready differentiated public-domain hardcover edition, with provenance intact, Irving's source text protected, compliant interior and case-laminate cover files, and all required publication metadata/evidence.

---

## Function 001 — Establish and protect authoritative source text

### BILL — SURVEY
Bill casts across the available function universe rather than preferring an inward or outward door.

**Inward findings**
- `books/sleepy-hollow/SOURCE.md` already records Project Gutenberg eBook #41 as the source.
- Existing rule: **MASTER NEVER WORKS. COPIES WORK.**
- `ASSEMBLY-MAP-001.json` already maps the working copy into stable paragraph IDs and reports 84 paragraphs / 12,225 words.
- Existing warehouse/research pieces include provenance fencing, verification state, text checking, text measurement, and warehouse promotion gates.

**Outward findings**
- Project Gutenberg eBook #41 identifies *The Legend of Sleepy Hollow* by Washington Irving and states it is public domain in the USA.
- Library of Congress item 00002099 provides a 1900 printed edition in digital form and states that the books in that collection are in the public domain and free to use/reuse.
- Amazon KDP permits public-domain works but may require proof and may refuse undifferentiated versions where a free version already exists. KDP explicitly recognizes an illustrated edition with 10 or more original relevant illustrations as one way to differentiate.

**Provenance chain**
1. Washington Irving work.
2. Project Gutenberg eBook #41 source record and text.
3. Anderson House `SOURCE.md` acquisition record.
4. Frozen master rule.
5. Working-copy descendants only.
6. Stable paragraph map / fingerprints.
7. Ted transformations logged separately.
8. Linda verification before promotion.

**Bill result:** SOURCE FUNCTION CANDIDATES SUFFICIENT.

### TED — BORG / BUILD
Ted does not replace the literary source. He reuses the existing source gate and wraps it in a hardcover-production provenance contract:
- preserve master source;
- operate on copies only;
- retain source record and public-domain evidence;
- retain a comparison source (Library of Congress) for integrity spot checks;
- record hashes/fingerprints for working states;
- require every later transform to state whether it changes Irving text or only presentation/supporting matter.

**Ted result:** REUSE + ADAPT EXISTING AH SOURCE/PROVENANCE FUNCTIONS.

### LINDA — VERIFY
Linda checks:
- source identity is documented;
- public-domain evidence exists;
- original text is protected from destructive production edits;
- provenance can be traced back to external source records;
- later changes can be distinguished from Irving's text.

**Status:** VERIFIED FOR CONTINUED PRODUCTION, subject to keeping hashes/records with actual production files.

**DOWNSTREAM STATE:** Verified protected source spine ready for hardcover-specific production.

---

## Function 002 — Convert the existing print route into a KDP hardcover route

### BILL — SURVEY

**Inward findings**
- Existing KDP print-contract candidates are explicitly `"format": "paperback"`.
- Existing 6 x 9 probe measured approximately **53 pages**.
- Existing KDP render gate is also principally a paperback adapter.

**Outward KDP findings (checked 2026-10-01)**
- KDP hardcover is **case laminate**; there is no dust jacket.
- KDP hardcover currently supports five trim sizes.
- For 6 x 9 in black ink on cream paper, allowed page count is **75–550 pages**.
- Hardcover requires separate interior and cover files.
- Exact cover dimensions depend on trim, paper/ink choices and **final page count**, so cover geometry must be calculated downstream.
- KDP's cover calculator/template is the authoritative geometry adapter.
- KDP public-domain policy means a differentiated edition is required if a free version exists; 10+ original relevant illustrations is an explicitly accepted differentiation route.

**Critical mismatch discovered**
Existing 6 x 9 print probe: ~53 pages.
KDP 6 x 9 hardcover minimum: 75 pages.

Therefore the existing paperback route cannot simply be relabeled hardcover.

**Bill result:** MISSING FUNCTION IDENTIFIED — HARDOVER PAGE-BUILD / EDITION-DESIGN FUNCTION that reaches >=75 pages without padding or corrupting the literary work.

### TED — NEXT BORG TARGET
Ted must build/adapt a hardcover edition structure that naturally crosses the 75-page minimum while improving the reader product. Candidate legitimate mechanisms include:
- 10+ original relevant illustrations (also satisfies KDP differentiation);
- appropriate front/back matter;
- typographic/layout choices suitable for a literary hardcover;
- optional original reader support only if it serves the agreed product and remains clearly separate from Irving's text.

Ted must **not** add meaningless blank/padded material merely to hit page count.

### LINDA — CURRENT GATE
Linda rejects direct reuse of the old 53-page 6 x 9 print route as a hardcover production contract.

**Status:** NEEDS BUILD / RECAST.

**DOWNSTREAM STATE NEEDED:** A prototype hardcover interior at a supported trim, at least 75 pages, with meaningful differentiated content and preserved source integrity.

---

## Current bridge picture

SOURCE / PROVENANCE
    |
    | VERIFIED
    v
PROTECTED WORKING COPY + STABLE STRUCTURE
    |
    | EXISTING
    v
HARDCOVER EDITION DESIGN  <--- CURRENT GAP
    |
    | must produce >=75 meaningful pages
    | and satisfy differentiated public-domain edition
    v
10+ ORIGINAL RELEVANT ILLUSTRATIONS + LAYOUT
    |
    v
FINAL PAGINATION
    |
    +--> margins / bleed verification
    +--> exact KDP hardcover cover calculator/template
    |
    v
INTERIOR PDF + CASE-LAMINATE COVER PDF
    |
    v
KDP PREVIEW / QA / METADATA / PUBLIC-DOMAIN EVIDENCE
    |
    v
VERIFIED UPLOAD-READY DONE

---

## Sources / chain-of-custody doors
- Project Gutenberg eBook #41: https://www.gutenberg.org/ebooks/41
- Library of Congress item 00002099: https://www.loc.gov/item/00002099/
- KDP public-domain policy: https://kdp.amazon.com/en_US/help/topic/G200743940
- KDP hardcover overview: https://kdp.amazon.com/en_US/help/topic/GAVW3FZZAKA2KY3B
- KDP trim / bleed / margins: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6/
- KDP hardcover formatting: https://kdp.amazon.com/en_US/help/topic/GKYZRXFBZH2LDXAK
- KDP cover calculator: https://kdp.amazon.com/en_US/cover-calculator
