## Why

PLANNING.md's Goal explicitly requires evaluating the system "with repeatable tests and measurable results," not just demonstrating it manually, and CLAUDE.md's Engineering Principles say to "measure behavior instead of relying on 'it feels good'" and never fabricate metrics. Right now the P0 core loop and P1 contradiction handling have only been verified by hand-run demo sessions and unit/integration tests against internal modules — there is no repeatable scenario suite that exercises the whole system end-to-end (CLI turn by turn) the way a real conversation would, and no measured pass rate to report.

## What Changes

- Add a scenario dataset (JSON/JSONL) of ~50 evaluation scenarios across 5 categories (10 each, per PLANNING.md's Evaluation Harness section): factual recall, long-range recall, contradiction/update, temporal reasoning, persona consistency. Each scenario is a sequence of conversation turns plus a final question and an expected outcome.
- Add an evaluation runner that replays each scenario's turns through the real `ConversationEngine` (a fresh per-scenario `MemoryStore`), asks the final question, and records the response.
- Add deterministic checks (substring/keyword-based, per PLANNING.md's "use deterministic checks for factual memory tests where possible") for the factual recall, long-range recall, contradiction/update, and temporal reasoning categories.
- Add an LLM-as-judge check (PASS/FAIL/PARTIAL) for the persona consistency category, with its documented limitations (judge bias, nondeterminism, evaluator/generation model correlation).
- Add metrics aggregation and a results report: per-category and overall pass rates, written from actual measured results only.
- Add failure logging: for each failed or partial scenario, record what was expected vs. what happened, feeding PLANNING.md's Failure Analysis.
- Add a runnable entry point (`python -m src.evaluation.run_eval`) writing results under `eval/results/`.

Out of scope for this change: baseline comparison against simpler architectures (PLANNING.md's Baseline A/B) — that needs separate baseline system variants and is left for a follow-up change; memory decay, hybrid retrieval reranking, `/memory-debug` and `/memory-timeline` commands (P3 differentiators).

## Capabilities

### New Capabilities
- `evaluation/scenario-dataset`: Defines the scenario schema and provides the ~50 scenarios across the 5 categories.
- `evaluation/eval-runner`: Executes scenarios end-to-end against the real conversation system and records a pass/fail/partial verdict per scenario, using deterministic checks where possible and an LLM judge for persona consistency.
- `evaluation/metrics-reporting`: Aggregates scenario results into per-category and overall measured metrics and a written results report, and logs failure detail for scenarios that did not pass.

### Modified Capabilities
(none — this change is purely additive; it exercises existing capabilities without changing their behavior)

## Impact

- New `src/evaluation/` module and `eval/scenarios/`, `eval/results/` directories, per CLAUDE.md's Repo Structure section.
- Running the harness makes real LLM/embedding calls (via the existing Groq/fastembed providers) for every scenario turn, so it has real latency and (free-tier) API usage - it is a manual/on-demand command, not part of the default `pytest` suite.
- No changes to `src/memory`, `src/chat`, `src/persona`, or `src/llm` behavior - the harness is a consumer of those modules, not a modification of them.
