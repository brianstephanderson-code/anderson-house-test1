# Sleepy Hollow — Reader Friction Survey 001

Status: DISPATCHED

Mailbox order: `hive/bus/orders/sleepy-hollow-reader-friction-survey-001.msg`

## Purpose
Survey the verified Project Gutenberg text of Washington Irving's *The Legend of Sleepy Hollow* for reader-friction candidates without modifying the source text.

## Source
Project Gutenberg eBook #41 plain-text edition:
https://www.gutenberg.org/files/41/41-0.txt

## Parent grammar
STATE → TRANSFORMATION → DONE

Fit Both Ways:
- IN ↔ OUT
- UP ↔ DOWN
- ORIGINATOR ↔ READER

## STATE
- Public-domain source text from Project Gutenberg.
- Source master is read-only for this survey.
- Reader Edition purpose: reduce unnecessary modern-reader friction while preserving Irving's text, tone, ambiguity, humor, pacing, and literary function.

## TRANSFORMATION
Survey the whole story and return candidates only. Do not insert annotations into the source.

Candidate classes:
1. archaic/unfamiliar vocabulary
2. historical people/events
3. place/geographic references
4. historical customs/material culture
5. literary/biblical/classical allusions
6. language whose apparent difficulty may itself be intentional literary function (false-positive/protection class)

For each candidate return:
- exact source locator or short identifying phrase
- class
- suspected reader obstruction
- suspected passage function
- FRICTION or FUNCTION or UNCERTAIN
- evidence needed
- proposed smallest support, if any

## Gates
- No annotation without a reader function.
- Use the smallest intervention that closes the reader gap.
- Do not annotate away productive ambiguity.
- Observable function may be stated; authorial intention requires evidence.
- Preserve uncertainty where evidence is uncertain.
- Gather evidence before drafting factual annotation text.
- Do not silently modernize, simplify, correct, or rewrite Irving.

## DONE
A candidate map suitable for evidence gathering and later annotation decisions, with the Irving source unchanged.

Status stays DISPATCHED until a correlated mailbox return proves completion.
This parcel is a production survey, not permission to publish or alter the source master.
