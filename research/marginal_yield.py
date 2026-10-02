#!/usr/bin/env python3
"""Measure useful-new evidence yield across route batch records.

Measurement only. This module never declares search DONE, sufficient, or true.
"""

from typing import Iterable, Mapping


def _count_useful_new(record: Mapping[str, object]) -> int:
    # route_batch_record currently exposes NEW refs and aggregate USEFUL count,
    # but not their intersection. Fail closed rather than invent that overlap.
    if "useful_new_count" not in record:
        raise ValueError("missing_required_field:useful_new_count")
    value = record["useful_new_count"]
    if not isinstance(value, int) or value < 0:
        raise ValueError("invalid:useful_new_count")
    return value


def marginal_yield(records: Iterable[Mapping[str, object]]) -> dict:
    """Return per-batch useful-new yield and a descriptive trend.

    All records must belong to one job and one route. Trend is measurement,
    not a continue/stop decision.
    """
    rows = list(records)
    if not rows:
        raise ValueError("no_batch_records")
    jobs = {r.get("job_id") for r in rows}
    routes = {r.get("route_id") for r in rows}
    if len(jobs) != 1 or None in jobs:
        raise ValueError("mixed_or_missing_job_id")
    if len(routes) != 1 or None in routes:
        raise ValueError("mixed_or_missing_route_id")

    yields = []
    for r in rows:
        fetched = r.get("fetched_count")
        if not isinstance(fetched, int) or fetched < 0:
            raise ValueError("invalid:fetched_count")
        useful_new = _count_useful_new(r)
        rate = (useful_new / fetched) if fetched else 0.0
        yields.append({"batch_id": r.get("batch_id"), "useful_new_count": useful_new,
                       "fetched_count": fetched, "yield_rate": rate})

    trend = "INSUFFICIENT_HISTORY"
    if len(yields) >= 2:
        a, b = yields[-2]["yield_rate"], yields[-1]["yield_rate"]
        trend = "RISING" if b > a else "FALLING" if b < a else "STABLE"
    return {"job_id": next(iter(jobs)), "route_id": next(iter(routes)),
            "batches": yields, "trend": trend}
