## 1. Generalize the Eval Runner

- [x] 1.1 Add an `engine_factory: Callable[[LLMProvider, EmbeddingProvider, MemoryStore], object]` parameter to `run_scenario`, defaulting to a factory that builds the proposed system's `ConversationEngine` (preserving current behavior), and verify existing `evaluation-harness` tests for `run_scenario` still pass unchanged
- [x] 1.2 Thread the same optional `engine_factory` parameter through `evaluate_scenario`, defaulting the same way, and verify existing `evaluate_scenario` tests still pass unchanged
- [x] 1.3 Verify a unit test: passing a custom factory (a minimal fake engine) causes `run_scenario` to drive that fake instead of the proposed system, with turns still sent in order

## 2. Baseline A: Context-Only, No Memory

- [x] 2.1 Implement `BaselineAEngine` (persona + full raw turn history + current message, no store, no extraction) with a `handle_message(str) -> str` method, and verify a unit test (mocked LLM) confirms no `MemoryStore` is ever touched and prior turns/responses appear in later calls' messages
- [x] 2.2 Add `baseline_a_factory(llm, embedder, store)` (ignoring `store`) usable as an `engine_factory`, and verify a unit test running a scenario through `run_scenario` with this factory produces a response with no memory persisted

## 3. Baseline B: Naive Vector Memory

- [x] 3.1 Implement `BaselineBEngine` reusing the proposed system's `MemoryExtractor`, `MemoryRetriever`, and `build_messages`, calling `extract_and_store(..., resolver=None)` so every SAVE candidate becomes a new ACTIVE row, and verify a unit test (mocked LLM) confirms a contradicted fact leaves both the original and the new memory ACTIVE and retrievable
- [x] 3.2 Add `baseline_b_factory(llm, embedder, store)` usable as an `engine_factory`, and verify a unit test running a scenario through `run_scenario` with this factory persists memories the same way the proposed system's extraction does, minus any supersede behavior

## 4. Comparison Reporting

- [x] 4.1 Implement `run_comparison(scenarios, llm, embedder, systems: dict[str, engine_factory]) -> dict[str, list[ScenarioResult]]` running every scenario against every named system, and verify a unit test with two fake systems confirms both get results for every scenario
- [x] 4.2 Implement `write_comparison_report(results_by_system, results_dir) -> Path` writing a JSON report with per-system, per-category, and overall pass rates plus a methodology note (naming which systems were run fresh vs reused from a prior canonical result), and verify a unit test confirms the written file contains all systems' metrics

## 5. Live Comparison Run

- [x] 5.1 Run Baseline A live against all 50 scenarios, budgeting API key usage as needed if a rate limit is hit (per design.md's key-rotation approach), and record the genuinely measured results. Hit the daily cap on the first key at scenario 5; restarted clean on a second key and completed all 50: 96% overall (48/50)
- [x] 5.2 Run Baseline B live against all 50 scenarios the same way, and record the genuinely measured results. Completed scenarios 1-33 cleanly before hitting a second key's daily cap; re-ran only the remaining 17 on a third key and combined with the first 33's real results: 96% overall (48/50)
- [x] 5.3 Combine Baseline A's and Baseline B's fresh results with the proposed system's existing canonical `evaluation-harness` results into one comparison report, and verify the report's numbers match each source (no numbers invented or adjusted). Written to `eval/results/comparison-20260902T054132Z.json`
- [x] 5.4 Write a short comparison write-up (which categories the proposed system's architecture measurably helped on, which it didn't, in plain terms) to inform the eventual README's "why hybrid memory was chosen" and "what alternatives were considered" sections - report what the numbers actually show, including if a baseline does surprisingly well somewhere. Written to `eval/BASELINE_COMPARISON.md`: both baselines score 96% vs the proposed system's 98% because scenarios are short enough to fit in raw context; digging into the one shared failure (`contra-08`) shows Baseline A gave a real non-answer (asked the user to disambiguate) while Baseline B's failure was a grading artifact (correct answer, unexpected wording) - documented plainly rather than glossed over

All 20 tasks complete.
