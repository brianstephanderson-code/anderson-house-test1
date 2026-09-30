# Sleepy Hollow — FINISHED-PRODUCT Full Policy Bridge Search — Lane A

Run date: 2026-09-30
Claim: `REPORTS/claims/sleepy-hollow-search-a-20260930-0528.claim`
Method: work backward from Reader Edition / KDP-ready DONE. Official/institutional and standards-facing gates only. Requirements translated into production FUNCTIONS. Contradictions and unresolved holes retained.

## DONE mould
A Sleepy Hollow Reader Edition that (1) has defensible rights/provenance, (2) satisfies current KDP public-domain admission/differentiation rules, (3) has accurate customer-facing metadata, (4) produces valid print and Kindle artifacts, (5) has working navigation/accessibility structure, and (6) survives prepublication QA without silently changing Irving's parent text.

## Hard gates → required functions

### A1 — Public-domain admission + differentiation
- SOURCE DOOR: Official / Amazon KDP — Publishing Public Domain Content; Content Guidelines. Checked 2026-09-30.
- EXACT REQUIREMENT: KDP permits public-domain content but may demand proof. If a free version is available in Amazon's store, KDP only accepts a differentiated version. KDP's enumerated qualifying differentiation is original translation, original annotation, or 10+ original relevant illustrations. Linked TOC, formatting improvements, collections, price, sales rank, and freely available Internet content do NOT qualify.
- FINISHED-PRODUCT WHY: A beautiful but undifferentiated Irving text can fail at the storefront gate.
- REQUIRED FUNCTION: `kdp_pd_admission_gate(work, marketplace_snapshot, provenance, differentiation_evidence) -> PASS|BLOCK + evidence_bundle`.
- DEPENDENCY: rights/provenance gate; edition-content inventory; current Amazon-store availability; differentiation ledger.
- FAILURE MODE: rejection/suppression because edition is undifferentiated or proof is missing.
- REUSE FIT-TEST: Existing generic `policy_audit` concept appears reusable as the audit shell, but only after fitting explicit KDP PD differentiation predicates and dated evidence capture. Do not treat formatting/TOC as differentiation.
- CONTRADICTION/VERSION NOTE: Public-domain legal status and KDP commercial admission are separate gates. A work can be legally PD yet still fail KDP's PD-product policy.

### A2 — Rights/provenance proof
- SOURCE DOOR: Official / U.S. Copyright Office — What Is Copyright?; Official / Project Gutenberg License + Permission How-to. Checked 2026-09-30.
- EXACT REQUIREMENT: U.S. Copyright Office states works published in the U.S. before 1931 are currently public domain. Project Gutenberg distinguishes unrestricted U.S. book text from its trademark/license wrapper; PG also warns some catalog items remain copyrighted and says to inspect the license inside the ebook. Commercial use of the Project Gutenberg trademark invokes separate terms; stripping PG license/references leaves unrestricted text for unrestricted works.
- FINISHED-PRODUCT WHY: The production line needs proof for the specific source/edition, not the folk rule “old book = public domain.”
- REQUIRED FUNCTION: `provenance_packet(source_file) -> identity + publication facts + PG license status + jurisdiction + copyright conclusion + retained evidence` and `strip_source_wrapper_without_touching_parent_text()`.
- DEPENDENCY: exact Gutenberg source identifier/file; source snapshot/hash; publication/edition facts; target marketplaces.
- FAILURE MODE: accidentally distributing copyrighted material, confusing PG trademark/license text with Irving text, or being unable to answer a KDP proof request.
- REUSE FIT-TEST: Provenance/integrity functions are conceptually reusable after fit-test; they must preserve source hash, extraction boundaries, and jurisdiction/date.
- CONTRADICTION/VERSION NOTE: Gutenberg's U.S.-focused unrestricted status does not itself prove worldwide PD status. KDP distributes internationally; marketplace-specific rights remain an unresolved gate below.

### A3 — KDP content/AI disclosure gate
- SOURCE DOOR: Official / Amazon KDP Content Guidelines. Checked 2026-09-30.
- EXACT REQUIREMENT: KDP requires disclosure of AI-generated text, images, or translations when publishing or republishing; AI-assisted content need not be disclosed. Publisher remains responsible for IP and all content rules.
- FINISHED-PRODUCT WHY: Reader Edition annotations/illustrations/translation created by generative AI change the submission declaration even when Irving's base text is PD.
- REQUIRED FUNCTION: `content_origin_ledger(component) -> human|AI-assisted|AI-generated + creator/tool + verification` then `kdp_ai_disclosure_answer(ledger)`.
- DEPENDENCY: component-level authorship trail for annotation, illustrations, translation, cover and interior art.
- FAILURE MODE: false KDP declaration; inability to distinguish generated content from assisted editing.
- REUSE FIT-TEST: QA/provenance ledger reusable after adding component origin classification.

### A4 — Metadata/product identity integrity
- SOURCE DOOR: Official / Amazon KDP Metadata Guidelines + Content Guidelines. Checked 2026-09-30.
- EXACT REQUIREMENT: title/subtitle together <200 characters; cover title/subtitle/author/series should match metadata; keywords/categories must not mislead/manipulate; print requires ISBN except specified exceptions; own ISBN in manuscript must match setup. Public-domain books are not eligible for KDP series creation. Translations must credit translator and original author; unknown non-new translator is listed as Anonymous.
- FINISHED-PRODUCT WHY: Product page, cover, interior and rights declaration must describe the same edition.
- REQUIRED FUNCTION: `metadata_crosscheck(interior, cover, kdp_fields) -> mismatches` plus `metadata_policy_gate()`.
- DEPENDENCY: final title/subtitle, contributors, edition type, cover, ISBN strategy, categories/keywords.
- FAILURE MODE: misleading listing, metadata rejection, ISBN mismatch, false contributor representation.
- REUSE FIT-TEST: Existing verification/cross-check functions should be reusable after schema fit-test.

### A5 — Print interior geometry gate
- SOURCE DOOR: Official / Amazon KDP Paperback Submission Guidelines; Set Trim Size, Bleed, and Margins. Checked 2026-09-30.
- EXACT REQUIREMENT: print interior is single pages, not spreads. No-bleed page size equals trim. Full bleed extends 0.125 in top/bottom/outside; manuscript page size is trim +0.125 in width and +0.25 in height. Minimum interior font 7 pt; fonts embedded. Outside margin minimum 0.25 in no bleed / 0.375 in bleed. Inside minimum varies by page count: 0.375 in (24–150), 0.5 (151–300), 0.625 (301–500), 0.75 (501–700), 0.875 (701–828).
- FINISHED-PRODUCT WHY: These are manufacturing acceptance constraints, not decoration.
- REQUIRED FUNCTION: `print_geometry_gate(pdf, trim, bleed, page_count) -> PASS|BLOCK + exact violations`.
- DEPENDENCY: final pagination comes before final gutter verification; trim/bleed decision precedes layout.
- FAILURE MODE: KDP Previewer errors, clipped content, wrong trim, insufficient gutter, unembedded fonts.
- REUSE FIT-TEST: Generic PDF/format verification may be reusable only if it can inspect MediaBox/TrimBox-like dimensions, margins and embedded fonts; otherwise new small checker needed.

### A6 — Print cover manufacturing gate
- SOURCE DOOR: Official / Amazon KDP Paperback Submission Guidelines. Checked 2026-09-30.
- EXACT REQUIREMENT: cover is one continuous image; layers flattened; 0.125 in bleed all sides; non-trim content at least 0.25 in from outside edge; fonts embedded. Spine width depends on page count and paper. Spine text prints only above 79 pages and requires clearance.
- FINISHED-PRODUCT WHY: Cover dimensions cannot be finalized independently of final page count/paper choice.
- REQUIRED FUNCTION: `cover_spec_compile(final_page_count, paper, trim) -> exact cover geometry` then `cover_gate(file, spec)`.
- DEPENDENCY: FINAL print pagination + paper/ink + trim before final cover.
- FAILURE MODE: cover rejection, shifted spine, unsafe text, wrong spine width.
- REUSE FIT-TEST: Dependency/order checker reusable; cover-specific geometry needs explicit predicates.

### A7 — Kindle format/validation gate
- SOURCE DOOR: Official / Amazon KDP supported eBook manuscript formats. Checked 2026-09-30.
- EXACT REQUIREMENT: EPUB is supported when it meets Kindle Publishing Guidelines; Amazon recommends validation with Kindle Previewer. MOBI fixed-layout uploads ceased acceptance effective March 2025. Other formats are accepted, but a Reader Edition should target a current reflowable EPUB path unless design requires otherwise.
- FINISHED-PRODUCT WHY: Source document is not the deliverable; the Kindle artifact must survive conversion/rendering.
- REQUIRED FUNCTION: `epub_build()` + `kindle_preview_gate(epub) -> render/navigation/errors` with dated format-policy check.
- DEPENDENCY: semantic structure, TOC, image accessibility, final content.
- FAILURE MODE: obsolete upload path, conversion defects, device rendering failure.
- REUSE FIT-TEST: Existing format conversion may be reusable; validation must be a separate gate.
- VERSION NOTE: MOBI fixed-layout change explicitly effective March 2025; retain date because accepted formats change.

### A8 — Kindle navigation gate
- SOURCE DOOR: Official / Amazon KDP Create a Table of Contents with Navigation Document; Navigation Guidelines. Checked 2026-09-30.
- EXACT REQUIREMENT: Amazon says all Kindle eBooks with chapters/sections require a working TOC; logical TOC is required for all Kindle books. TOC links must work and target correct locations; chapter/section entries/names/order must match. HTML TOC is strongly recommended and should be near the beginning; page numbers should not be used in Kindle TOC.
- FINISHED-PRODUCT WHY: Navigation is part of the Reader Edition's functional DONE, not cosmetic formatting.
- REQUIRED FUNCTION: `semantic_section_map(parent_text)` -> canonical IDs/headings; `kindle_nav_build(map)`; `nav_integrity_gate(epub,map)`.
- DEPENDENCY: stable section boundaries/headings before nav compilation.
- FAILURE MODE: grayed-out Go To, broken links, missing sections, wrong targets, reader progress/navigation defects.
- REUSE FIT-TEST: Structure/verification functions likely reusable after exact link-target and coverage checks.
- CONTRADICTION NOTE: One KDP Navigation Guidelines page says complete NCX is required, while the newer TOC guidance recommends EPUB navigation document and says NCX remains supported but navigation document is preferred. Preserve both; target EPUB nav + logical TOC, optionally NCX as compatibility output rather than treating NCX-only as the modern mould.

### A9 — Accessibility semantics gate
- SOURCE DOOR: Official / Amazon KDP Accessibility Guidelines. Checked 2026-09-30.
- EXACT REQUIREMENT/RECOMMENDATION: define primary language/language changes; hierarchical headings; semantic lists; meaningful-image text alternatives and null alt for decorative images; avoid images of text; self-describing links; adequate contrast (KDP cites WCAG 4.5:1 recommendation); tables need captions/row/column headings; reading order matters in fixed-layout.
- FINISHED-PRODUCT WHY: Reader Edition should remain usable with assistive technology; semantic structure also improves navigation/conversion robustness.
- REQUIRED FUNCTION: `accessibility_semantics_gate(epub_source) -> language + heading hierarchy + alt coverage + link labels + contrast/table/read-order findings`.
- DEPENDENCY: content-origin/illustration inventory and semantic section map.
- FAILURE MODE: inaccessible images/structure, poor screen-reader navigation, ambiguous links.
- REUSE FIT-TEST: QA shell reusable; accessibility checks require dedicated predicates.
- STATUS NOTE: KDP phrases much of this as best practice/recommendation, not every item as an upload rejection criterion. Keep HARD KDP gates distinct from Reader Edition quality gates.

## Backward dependency chain
`KDP-READY DONE` <- final Preview/QA <- {print PDF gate, cover gate, Kindle EPUB/nav/accessibility gate, metadata crosscheck} <- stable final content + pagination <- {differentiation evidence, content-origin ledger, parent-text integrity} <- provenance/rights packet <- exact source acquisition.

Critical ordering discovery: FINAL PAGINATION is a join. It determines print gutter class and cover spine geometry. Therefore cover-finalization cannot safely run in parallel with unresolved pagination.

## Existing-function fit-test summary
Potentially reusable families (names/concepts observed historically in Anderson House): policy audit; integrity verification; cross-check/QA; provenance; routing/closure. Reuse is conditional: each must be tested against the explicit predicates above. Do not reuse by name alone. No repository code-search hit was found for a dedicated Sleepy Hollow/KDP provenance implementation in this run.

## Unresolved holes / coordinator recast
1. WORLDWIDE RIGHTS: establish intended KDP marketplaces, then prove Irving/Sleepy Hollow rights per marketplace. U.S. PD proof alone is insufficient for global distribution.
2. SOURCE-SPECIFIC PROVENANCE: capture exact Gutenberg ebook ID/file/version/hash and inspect its embedded license/header. This run researched policy, not a specific source artifact.
3. DIFFERENTIATION DESIGN: decide the Reader Edition's qualifying KDP differentiation (original annotation vs 10+ original illustrations vs original translation). “Reader-friendly formatting” alone is explicitly insufficient.
4. ACCESSIBILITY STANDARD DEPTH: reconcile KDP recommendations with current EPUB Accessibility/WCAG standards in a standards-specialist cast; this lane established the KDP-facing minimum only.
5. PRINT PRODUCT CHOICES: trim, paper/ink, bleed, paperback vs hardcover and expected page count remain inputs before exact print/cover mould can be frozen.
6. KINDLE GUIDELINE VERSIONING: capture the current downloadable Kindle Publishing Guidelines/version identifier if a durable PDF/manual is needed for audit; web help pages can change.
7. CUSTOMER/END-USER FUNNEL intentionally not claimed here; Lane A was official/institutional finished-product gates.

## Source URLs / doors
- Amazon KDP — Publishing Public Domain Content: https://kdp.amazon.com/en_US/help/topic/G200743940
- Amazon KDP — Content Guidelines: https://kdp.amazon.com/en_US/help/topic/G200672390
- Amazon KDP — Paperback Submission Guidelines: https://kdp.amazon.com/en_US/help/topic/G201857950
- Amazon KDP — Set Trim Size, Bleed, and Margins: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6/
- Amazon KDP — Accessibility Guidelines: https://kdp.amazon.com/en_US/help/topic/GF9Z3HLUMTRJ6QPL
- Amazon KDP — Navigation Guidelines: https://kdp.amazon.com/en_US/help/topic/GY3AD8C6C6GAG42N
- Amazon KDP — Create a TOC with Navigation Document: https://kdp.amazon.com/en_US/help/topic/G201605710
- Amazon KDP — Metadata Guidelines: https://kdp.amazon.com/en_US/help/topic/G201097560
- Amazon KDP — Supported eBook manuscript formats: https://kdp.amazon.com/en_US/help/topic/G200634390
- U.S. Copyright Office — What Is Copyright?: https://www.copyright.gov/what-is-copyright/
- Project Gutenberg — License: https://www.gutenberg.org/policy/license
- Project Gutenberg — Permission How-to: https://www.gutenberg.org/policy/permission

STATUS=RETURNED_TO_COORDINATOR
