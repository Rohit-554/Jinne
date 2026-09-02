## 1. Architecture Documentation

- [x] 1.1 Write `ARCHITECTURE.md`: component diagram (conversation engine, persona manager, extractor, resolver, store, retriever, evaluation harness), data flow through a turn, and the "embeddings are not the source of truth" architectural statement from PLANNING.md

## 2. README

- [x] 2.1 Write `README.md` covering: problem statement, how to run (setup, `.env`, `python -m src.cli`), architecture summary (linking to `ARCHITECTURE.md`), memory model, extraction strategy, retrieval strategy, contradiction handling, temporal memory, persona consistency
- [x] 2.2 Add "why hybrid memory was chosen" and "what alternatives were considered" sections, drawing on `eval/BASELINE_COMPARISON.md`'s real results
- [x] 2.3 Add "evaluation methodology and actual results" and "known limitations" sections, drawing on `eval/FAILURE_ANALYSIS.md` and the evaluation-harness/baseline-comparison canonical reports - real numbers only
- [x] 2.4 Add a "next improvements" section (entity-overlap retrieval scoring, tunable decay/score weights, `/eval` as an in-CLI command, further failure analysis categories)

## 3. Demo Script

- [x] 3.1 Write a step-by-step demo script section (session 1: state facts; restart; session 2: recall, contradict, recall update and history; run `/memories` and `/memory-debug`), following PLANNING.md's Demo Story

## 4. Final Verification (covers this and all prior undone phases)

- [x] 4.1 Run the full pytest suite for the whole project (Phase 1 decay/scoring tests, Phase 2 CLI/explainability tests, and everything preexisting) and fix any failures
- [x] 4.2 Live-run the demo script exactly as written against the real CLI and correct the README/demo text wherever actual output differs from what was drafted. Ran both sessions live end-to-end (restart between them); the scripted flow matched actual CLI behavior - no demo text corrections were needed
- [x] 4.3 Live-verify `/memories` and `/memory-debug` produce sensible output during the demo run. Both worked correctly; the live run also surfaced a real resolver limitation (relation-label-exact matching missing a semantically-linked contradiction), documented in README.md's Known Limitations and Next Improvements rather than patched under time pressure
- [x] 4.4 Commit and push all of Phase 1 (memory-decay-and-reranking), Phase 2 (memory-explainability-cli), and Phase 3 (project-documentation) once verified
