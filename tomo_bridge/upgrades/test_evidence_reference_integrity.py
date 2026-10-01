#!/data/data/com.termux/files/usr/bin/python
"""Zero-network regression tests for claim/source reference integrity."""
from evidence_reference_integrity import evidence_reference_failures


def main():
    sources = {
        "good": {"id": "good", "url": "https://example.gov.au/rule"},
        "empty": {"id": "empty", "url": ""},
    }

    assert evidence_reference_failures(
        [{"text": "good claim", "source_ids": ["good"]}], sources
    ) == []

    failures = evidence_reference_failures(
        [{"text": "dangling claim", "source_ids": ["missing"]}], sources
    )
    assert failures[0]["missing_source_ids"] == ["missing"], failures

    failures = evidence_reference_failures(
        [{"text": "empty URL", "source_ids": ["empty"]}], sources
    )
    assert failures[0]["empty_url_source_ids"] == ["empty"], failures

    failures = evidence_reference_failures(
        [{"text": "uncited claim", "source_ids": []}], sources
    )
    assert failures[0]["no_source_ids"] is True, failures

    print("PASS: claim/source reference integrity regression suite")


if __name__ == "__main__":
    main()
