## Why

PLANNING.md's README Must Explain section lists what the final README needs to cover, and Final Positioning is explicit that the submission should read as "a temporal memory architecture... evaluated," not just a chatbot demo. All the substance to support that positioning now exists (P0-P2 changes plus this P3 work), but it is scattered across `PLANNING.md`, `CLAUDE.md`, and per-change `design.md`/`FAILURE_ANALYSIS.md`/`BASELINE_COMPARISON.md` files - there is no single entry point a reviewer can read to understand the project, run it, and see the actual measured results.

## What Changes

- Write `README.md` covering: the problem, how to run the project, architecture, memory model, extraction/retrieval/contradiction strategy, temporal memory, persona consistency, why hybrid memory was chosen and what alternatives were considered (drawing on `eval/BASELINE_COMPARISON.md`), evaluation methodology and actual results (drawing on `eval/FAILURE_ANALYSIS.md`), known limitations, and next improvements - per PLANNING.md's README Must Explain section, using only real, already-measured numbers.
- Write `ARCHITECTURE.md` with the component diagram and data-flow explanation (conversation engine, persona manager, extractor, resolver, store, retriever, evaluation harness) and the "embeddings are not the source of truth" architectural statement from PLANNING.md.
- Write a scripted demo walkthrough (as part of the README or a dedicated section) following PLANNING.md's Demo Story: tell the companion facts, restart, recall, contradict, recall the update and the history, run `/memories` and `/memory-debug`.

This is a documentation-only change - `skip_specs: true`, since no system behavior changes.

## Capabilities

(none - documentation only, per `skip_specs: true` above)

## Impact

- New `README.md` and `ARCHITECTURE.md` at the repo root, per CLAUDE.md's Repo Structure section.
- No code changes.
