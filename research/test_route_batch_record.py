#!/usr/bin/env python3
"""Linda regression tests for route_batch_record."""

import unittest

from route_batch_record import route_batch_record


class RouteBatchRecordTests(unittest.TestCase):
    def test_categories_and_counts_remain_separate(self):
        items = [
            {"evidence_ref": "e1", "provenance_ref": "p1", "source_family": "official", "judgment": "USEFUL", "novelty": "NEW"},
            {"evidence_ref": "e2", "provenance_ref": "p2", "source_family": "community", "judgment": "NOT_USEFUL", "novelty": "PREVIOUSLY_SEEN"},
            {"evidence_ref": "e3", "provenance_ref": "p3", "source_family": "archive", "judgment": "UNJUDGED", "novelty": "UNKNOWN"},
        ]
        r = route_batch_record("job", "route", "batch", items)
        self.assertEqual(r["fetched_count"], 3)
        self.assertEqual(r["judged_count"], 2)
        self.assertEqual(r["useful_count"], 1)
        self.assertEqual(r["not_useful_count"], 1)
        self.assertEqual(r["unjudged_count"], 1)
        self.assertEqual(r["new_evidence_refs"], ("e1",))
        self.assertEqual(r["previously_seen_refs"], ("e2",))
        self.assertNotIn("e3", r["new_evidence_refs"])

    def test_invalid_judgment_fails_closed(self):
        item = {"evidence_ref": "e", "provenance_ref": "p", "source_family": "f", "judgment": "MAYBE", "novelty": "NEW"}
        with self.assertRaises(ValueError):
            route_batch_record("job", "route", "batch", [item])

    def test_invalid_novelty_fails_closed(self):
        item = {"evidence_ref": "e", "provenance_ref": "p", "source_family": "f", "judgment": "USEFUL", "novelty": "SORT_OF_NEW"}
        with self.assertRaises(ValueError):
            route_batch_record("job", "route", "batch", [item])

    def test_empty_batch_is_measurement_only(self):
        r = route_batch_record("job", "route", "batch", [])
        self.assertEqual(r["fetched_count"], 0)
        self.assertNotIn("done", r)
        self.assertNotIn("stop", r)
        self.assertNotIn("sufficient", r)

    def test_missing_identity_or_provenance_fails_closed(self):
        with self.assertRaises(ValueError):
            route_batch_record("", "route", "batch", [])
        item = {"evidence_ref": "e", "provenance_ref": "", "source_family": "f", "judgment": "USEFUL", "novelty": "NEW"}
        with self.assertRaises(ValueError):
            route_batch_record("job", "route", "batch", [item])


if __name__ == "__main__":
    unittest.main()
