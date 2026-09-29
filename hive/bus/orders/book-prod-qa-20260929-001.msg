MESSAGE_ID=book-prod-qa-20260929-001
CORRELATION_ID=book-prod-qa-20260929-001
CHANNEL=ORDERS
FROM=MANAGEMENT
TO=ALL
TYPE=BOOK_PRODUCTION_QA
FUNCTION=character_count
PURPOSE=Exercise the newly wired character-count function as a real Gutenberg-to-KDP production QA primitive, independently across provider lanes, preserving exact identity and evidence for closure.
INPUT_TEXT=It was the best of times, it was the worst of times.
EXPECTED_CHARACTER_COUNT=51
DONE=Each provider returns STATUS=DONE with the same MESSAGE_ID/CORRELATION_ID and a character-count result; closure clerk marries all returns to the master and retires copies into warehouse evidence.
POLICY=SMALL_COMPOSABLE_FUNCTION;MASTER_STAYS_WITH_WORK;COPIES_TRAVEL;NO_SYNTHETIC_BUSYWORK
UTC=2026-09-29T16:32:29Z
