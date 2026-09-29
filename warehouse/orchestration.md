# Shelf: Orchestration

Purpose: functions that fan work out to smaller functions and join the answers.

- provider_hive
  - Source: function-lane/core/provider_hive.mjs
  - Proof: function-lane/test/google_hive.test.mjs
  - Current children: word_count, sentence_count, paragraph_count, terminal_punctuation, character_count, line_count, blank_line_count
  - Mode: fanout-join
  - Status: TEST-PRESENT
