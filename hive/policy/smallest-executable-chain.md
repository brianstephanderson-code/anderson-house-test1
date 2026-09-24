# Anderson House — Smallest Executable Chain Policy

Status: ACTIVE CANDIDATE POLICY
Added: 2026-09-23

## Purpose
Reduce worker understanding, human touch, and failure surface by making each production movement as small and explicit as useful.

## Core
Use the smallest useful chain:

SMALLEST USEFUL STATE -> SMALLEST USEFUL TRANSFORM -> SMALLEST USEFUL DONE.

Then let that DONE become the next STATE.

## Parent relationship
Every micro-DONE must point upward to a parent DONE.
Do not optimize a tiny step that no longer advances the parent objective.

## Placement rule
Place the transformation at the natural joint immediately before the next state begins.
Complete and verify that joint before downstream work assumes it happened.

## Worker rule
A worker should need to understand only the parcel, function, constraints, and acceptance test required for its local DONE.
Do not require the worker to understand the whole organization when a deterministic local contract is sufficient.

## Verification rule
Verify each important joint as cheaply as practical:
- expected output exists;
- count/identity matches;
- acceptance condition passes;
- state is durable enough for the next worker.

## Reconstruction
Chain verified micro-DONEs upward until the parent DONE is satisfied and independently recognizable.

## Shorthand
SMALL STATE -> SMALL DO -> SMALL DONE -> NEXT STATE.
LOCAL CERTAINTY -> PARENT DONE.
