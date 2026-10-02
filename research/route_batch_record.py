#!/usr/bin/env python3
"""Record what one evidence-fenced retrieval batch contributed.

Measurement only: this function does not decide truth, sufficiency, diversity,
or whether searching should stop. Evidence items are referenced, not rewritten.
"""

from dataclasses import dataclass, asdict
from typing import Iterable, Mapping

JUDGMENTS = frozenset({"USEFUL", "NOT_USEFUL", "UNJUDGED"})
NOVELTY = frozenset({"NEW", "PREVIOUSLY_SEEN", "UNKNOWN"})


@dataclass(frozen=True)
class RouteBatchRecord:
    job_id: str
    route_id: str
    batch_id: str
    fetched_count: int
    judged_count: int
    useful_count: int
    not_useful_count: int
    unjudged_count: int
    new_evidence_refs: tuple[str, ...]
    previously_seen_refs: tuple[str, ...]
    source_family_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]


def _need_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing_or_invalid:{name}")
    return value.strip()


def route_batch_record(job_id: str, route_id: str, batch_id: str,
                       items: Iterable[Mapping[str, object]]) -> dict:
    """Return an immutable-shaped measurement record for one fenced batch.

    Each item requires evidence_ref, provenance_ref, judgment, novelty, and
    source_family. UNKNOWN novelty is intentionally not counted as new.
    """
    job_id = _need_text("job_id", job_id)
    route_id = _need_text("route_id", route_id)
    batch_id = _need_text("batch_id", batch_id)
    rows = list(items)

    useful = not_useful = unjudged = 0
    new_refs: list[str] = []
    seen_refs: list[str] = []
    families: set[str] = set()
    provenance: set[str] = set()

    for i, item in enumerate(rows):
        ref = _need_text(f"items[{i}].evidence_ref", item.get("evidence_ref"))
        prov = _need_text(f"items[{i}].provenance_ref", item.get("provenance_ref"))
        family = _need_text(f"items[{i}].source_family", item.get("source_family"))
        judgment = item.get("judgment")
        novelty = item.get("novelty")
        if judgment not in JUDGMENTS:
            raise ValueError(f"invalid_judgment:{i}")
        if novelty not in NOVELTY:
            raise ValueError(f"invalid_novelty:{i}")

        if judgment == "USEFUL": useful += 1
        elif judgment == "NOT_USEFUL": not_useful += 1
        else: unjudged += 1

        if novelty == "NEW": new_refs.append(ref)
        elif novelty == "PREVIOUSLY_SEEN": seen_refs.append(ref)
        families.add(family)
        provenance.add(prov)

    record = RouteBatchRecord(
        job_id=job_id, route_id=route_id, batch_id=batch_id,
        fetched_count=len(rows), judged_count=useful + not_useful,
        useful_count=useful, not_useful_count=not_useful,
        unjudged_count=unjudged,
        new_evidence_refs=tuple(new_refs),
        previously_seen_refs=tuple(seen_refs),
        source_family_refs=tuple(sorted(families)),
        provenance_refs=tuple(sorted(provenance)),
    )
    return asdict(record)
