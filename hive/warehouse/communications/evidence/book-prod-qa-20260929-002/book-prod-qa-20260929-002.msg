MESSAGE_ID=book-prod-qa-20260929-002
CORRELATION_ID=book-prod-qa-20260929-002
CHANNEL=ORDERS
FROM=MANAGEMENT
TO=ALL
TYPE=BOOK_PRODUCTION_QA
FUNCTION=character_count
PAYLOAD=It was the best of times, it was the worst of times.
EXPECTED_CHARACTER_COUNT=52
DONE=All three providers return correlated STATUS=DONE with characters=52; closure marries copies back to the master and archives them.
POLICY=SMALL_COMPOSABLE_FUNCTION;MASTER_STAYS_WITH_WORK;COPIES_TRAVEL;SEMANTIC_RESULT_MUST_VERIFY
UTC=2026-09-29T20:39:30Z
