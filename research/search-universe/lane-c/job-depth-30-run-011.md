# Anderson House — Search Universe Lane C

Run: 011
Job depth: 30
Status: PENDING — queue intentionally retained for subsequent runs
Purpose: harvest materially distinct, reusable, composable search functions.

## Queue

1. OCR-confusion recast — DONE
2. Exact→proximity ladder — DONE
3. Bibliographic-field isolation — DONE
4. Catalog identity pivot — DONE
5. Code symbol/regex pivot — DONE
6. Cross-era vocabulary ladder — DONE
7. Edition/reproduction bridge — DONE
8. Metadata→carrier pivot — DONE
9. Negative-term contrast cast — DONE
10. Geography/time intersection — DONE
11. Citation-backchain — PENDING
12. Citation-forward-chain — PENDING
13. Author identity/disambiguation — PENDING
14. Institutional lineage/name-change — PENDING
15. Dead URL→archive wildcard — PENDING
16. Filename/path fossil search — PENDING
17. Manual error-string pivot — PENDING
18. Standards/version pivot — PENDING
19. Patent prior-art vocabulary — PENDING
20. Thesis/dissertation pivot — PENDING
21. Subject-heading translation — PENDING
22. Multilingual terminology pivot — PENDING
23. Table-of-contents/chapter pivot — PENDING
24. Image-caption/figure-label pivot — PENDING
25. Dataset/code companion pivot — PENDING
26. Commit-history/diff search — PENDING
27. Forum symptom→maintainer terminology bridge — PENDING
28. Entity-neighbor/co-occurrence cast — PENDING
29. Contradiction/failure-case cast — PENDING
30. Independent-oracle convergence cast — PENDING

## Harvested reusable functions

### C01 OCR-confusion recast
Purpose: recover historical hits hidden by OCR or historical spelling.
STATE/input: a name/phrase with sparse archive results.
Doors/casts: historical newspapers/OCR corpora; generate likely letterform, diacritic, spelling and typography variants; constrain by place/date/language.
Transformation: canonical term → plausible transcription variants → grouped searches → page-image confirmation.
DONE/output: confirmed hit plus productive variant vocabulary.
Stop/sufficiency: stop when page image confirms target and additional variants cease adding materially new evidence.
Dependencies: OCR corpus + image access where possible.
Failure boundary: snippet/OCR alone is not proof.
Fit-test: reuse when scanned historical text is involved and exact spelling underperforms.
Evidence: LOC NDNP confirms searchable digitized historical newspaper corpus; observed specialist methodology documents OCR-confusion/variant searching.

### C02 Exact→proximity ladder
Purpose: rescue concepts whose words drift in order or spacing.
STATE/input: exact phrase gives too few/no hits.
Doors/casts: exact phrase → proximity window → AND terms → controlled synonyms.
Transformation: progressively relax adjacency while preserving semantic anchors.
DONE/output: evidence containing the required terms in a contextually meaningful neighborhood.
Stop/sufficiency: first rung with enough relevant evidence; do not widen further unless coverage remains insufficient.
Dependencies: engine supporting phrase/proximity/Boolean search.
Failure boundary: widening can create semantic false positives; inspect context.
Fit-test: reusable for academic, OCR and prose corpora.
Evidence: OpenAlex supports exact, Boolean and proximity search.

### C03 Bibliographic-field isolation
Purpose: find a work when generic full-text search is noisy.
STATE/input: partial title/author/journal/year/reference string.
Doors/casts: bibliographic-only fields; date filters; selected response fields.
Transformation: loose citation clues → structured bibliographic query → stable identifier.
DONE/output: DOI/record or uniquely identified work.
Stop/sufficiency: identifier + metadata agree on distinguishing fields.
Dependencies: bibliographic index/API.
Failure boundary: malformed or incomplete citations can still collide; independently check title/author/year.
Fit-test: reusable for papers, references and citation reconstruction.
Evidence: Crossref exposes bibliographic queries, filters and selective fields.

### C04 Catalog identity pivot
Purpose: turn vague book/object clues into a stable bibliographic identity and new search vocabulary.
STATE/input: title fragment, author, date, publisher, subject, format or collection clue.
Doors/casts: library catalog; edition/format list; subject headings; identifiers.
Transformation: loose clue → catalog record → OCLC/ISBN/subjects/edition relationships → recast those anchors elsewhere.
DONE/output: stable identity plus harvested vocabulary/identifiers.
Stop/sufficiency: distinguishing metadata converges sufficiently to identify the intended object.
Dependencies: catalog coverage.
Failure boundary: similarly titled works/editions; preserve edition distinction.
Fit-test: books, manuals, catalogs, historical objects.
Evidence: WorldCat records expose editions/formats, OCLC identifiers, subjects, notes and linked reproductions.

### C05 Code symbol/regex pivot
Purpose: find an implementation when prose/name search is inadequate.
STATE/input: behavior, symbol fragment, error phrase, filename clue or syntax shape.
Doors/casts: symbol search; regex; Boolean; language/repository/file narrowing.
Transformation: behavior clue → likely code tokens/pattern → symbol/regex cast → implementation context.
DONE/output: concrete implementation/function plus repository context.
Stop/sufficiency: implementation and surrounding code establish the required function; compare another implementation when correctness matters.
Dependencies: indexed source repositories.
Failure boundary: copied/dead/example code can masquerade as production practice.
Fit-test: software functions, parsers, protocol behavior, error handling.
Evidence: GitHub Code Search documents regex, Boolean operators, symbol/file navigation and multi-repository search.

### C06 Cross-era vocabulary ladder
Purpose: bridge modern wording to older terminology.
STATE/input: modern concept with weak older-web/archive recall.
Doors/casts: modern term → catalog subjects → period synonyms → obsolete technical/trade terminology → dated corpus searches.
Transformation: present vocabulary → historically plausible vocabulary families.
DONE/output: period-appropriate terms that materially improve retrieval.
Stop/sufficiency: at least one older term repeatedly retrieves relevant period evidence and new terms stop changing the evidence picture.
Dependencies: dated catalogs/corpora and historical context.
Failure boundary: anachronism; never infer equivalence from lexical similarity alone.
Fit-test: old manuals, newspapers, books, trades, technology history.

### C07 Edition/reproduction bridge
Purpose: move from an inaccessible edition to another carrier containing the same work.
STATE/input: identified work but poor/no access.
Doors/casts: editions/formats; reproduction notes; print-version links; digital repositories.
Transformation: work identity → edition/reproduction relationships → accessible carrier.
DONE/output: inspectable equivalent or clearly related edition with provenance preserved.
Stop/sufficiency: accessible carrier matches required content/edition constraints.
Dependencies: catalog linkage and repository availability.
Failure boundary: revisions/abridgments can differ; do not silently treat every edition as text-identical.
Fit-test: books, theses, manuals, public-domain source verification.
Evidence: WorldCat records can expose print-version and electronic-reproduction relationships.

### C08 Metadata→carrier pivot
Purpose: use a thin index record as a bridge rather than treating it as the final evidence.
STATE/input: metadata-only hit.
Doors/casts: extract identifier, publisher, collection, date, repository/reproduction link; search those anchors in carrier repositories.
Transformation: descriptive record → carrier-location clues → primary/digitized object.
DONE/output: inspectable source or documented access boundary.
Stop/sufficiency: carrier is found and inspected, or multiple independent location clues establish that access is unavailable.
Dependencies: stable identifiers/metadata quality.
Failure boundary: metadata errors propagate; confirm against carrier when possible.
Fit-test: catalogs, archive finding aids, bibliographic databases.

### C09 Negative-term contrast cast
Purpose: remove a dominant wrong universe without over-narrowing the positive query.
STATE/input: query swamped by a recurring irrelevant meaning/entity.
Doors/casts: positive anchors + NOT/excluded terms; compare excluded vs unexcluded result sets.
Transformation: noisy candidate pool → contrastive pool.
DONE/output: materially higher relevant-hit ratio without losing known good controls.
Stop/sufficiency: known positives remain and dominant false-positive class drops materially.
Dependencies: Boolean/exclusion support.
Failure boundary: excluded term may also occur in genuine evidence; retain control searches.
Fit-test: ambiguous names, homonyms, overloaded technical terms.
Evidence: OpenAlex and GitHub document Boolean exclusion/NOT capabilities.

### C10 Geography/time intersection
Purpose: turn a common name/event into a tractable historical search.
STATE/input: common entity plus approximate place/time.
Doors/casts: name/variant × locality × bounded dates; widen one dimension at a time.
Transformation: high-entropy identity query → spatiotemporally constrained candidate set.
DONE/output: small reviewable set with contextual corroboration.
Stop/sufficiency: distinguishing contextual facts converge; widen only the dimension shown to be uncertain.
Dependencies: sources carrying place/date metadata.
Failure boundary: newspapers can report nonlocal events; location is a filter, not identity proof.
Fit-test: genealogy, historical events, local businesses/institutions, old advertisements.

## Coordinator reconciliation

The ten functions are materially different: corruption recovery (C01), adjacency relaxation (C02), structured field isolation (C03), identity stabilization (C04), implementation search (C05), temporal vocabulary translation (C06), carrier substitution (C07), metadata-to-primary bridging (C08), false-universe subtraction (C09), and spatiotemporal narrowing (C10).

Reusable composite discovered without fusing the atoms:
STATE → identity anchors (C04/C03) → vocabulary bridge (C06/C01) → precision/recall ladder (C02/C09/C10) → carrier bridge (C08/C07) → inspect primary evidence → DONE.

No fixed composite function adopted. Each function remains independently replaceable/testable.

Next frontier: C11 citation-backchain through C20 thesis/patent/standards doors, then C21–C30 cross-language, structural, code-history, contradiction and independent-oracle patterns.
