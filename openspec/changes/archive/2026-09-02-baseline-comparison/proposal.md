## Why

PLANNING.md's Baseline Comparison section exists to answer a specific question the assignment cares about: does the hybrid structured-memory architecture (SQLite status/lifecycle + semantic retrieval + LLM resolver) actually produce better measurable behavior than simpler approaches, or is it unnecessary complexity? `evaluation-harness` built the scenario suite and grading logic needed to answer this rigorously but explicitly deferred it. With that harness now proven (98% pass on the proposed system), running the same 50 scenarios against two simpler baselines is a small additional step that turns "we built something more complex" into "we measured that the complexity earns its keep" - the exact framing PLANNING.md's Final Positioning asks for.

## What Changes

- Add **Baseline A** (conversation context only, no persistent memory): each turn sends the persona and the full raw conversation history so far, with no extraction, no retrieval, no storage at all.
- Add **Baseline B** (naive vector memory): every SAVE-worthy extracted fact is embedded and stored, retrieved every turn purely by cosine similarity across everything ever stored - no lifecycle status, no resolver, no contradiction handling, so a superseded fact stays just as retrievable as its replacement.
- Generalize the eval runner so the same scenario dataset can run against any of the three systems (proposed system, Baseline A, Baseline B) via a pluggable engine factory, instead of being hardcoded to the proposed system's `ConversationEngine` + resolver.
- Add a comparison report: run all 50 scenarios against all three systems and produce a side-by-side per-category and overall pass-rate table, from real measured results only.

Out of scope: changing the proposed system itself; the baselines are throwaway comparison scaffolding, not alternative production code paths.

## Capabilities

### New Capabilities
- `evaluation/baseline-systems`: Baseline A (context-only) and Baseline B (naive vector memory) conversation engines, usable as drop-in alternatives to the proposed system for evaluation.
- `evaluation/comparison-reporting`: Runs the scenario suite against multiple systems and produces a comparative report of measured results.

### Modified Capabilities
- `evaluation/eval-runner`: `run_scenario`/`evaluate_scenario` generalized to accept a pluggable engine factory, so they are not hardcoded to the proposed system's `ConversationEngine`.

## Impact

- Purely additive to evaluation tooling under `src/evaluation/`; no change to `src/memory`, `src/chat`, `src/persona`, or `src/llm` behavior.
- Running the comparison makes real LLM/embedding calls for all three systems across all 50 scenarios (roughly 3x the token cost of one `evaluation-harness` run), so it is a manual/on-demand command, mindful of the free-tier daily token cap already observed during `evaluation-harness`.
