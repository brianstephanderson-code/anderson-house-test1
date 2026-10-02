# Three Amigos — Vexy production door

This is a reusable production function, not a personal bookmark.

Flow:

APPROVED MASTER -> VEXY FUNCTION -> SVG + PREVIEW + REPORT -> LINDA VERIFY -> WAREHOUSE

Sleepy Hollow is the first production customer.

The source master stays untouched. Vexy operates on the repository copy at the path named in the job record.

A job is DONE only when the repository contains:
- output.svg
- preview.png
- report.json

Linda then verifies the output before it is accepted into the finished-art warehouse.
