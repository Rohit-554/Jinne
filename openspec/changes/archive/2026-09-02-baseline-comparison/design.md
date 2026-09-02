## Context

`evaluation-harness` proved the proposed system scores 98% (49/50) on the 50-scenario suite. That number is meaningless as an argument for the architecture's *design* without something to compare it against - PLANNING.md's Baseline Comparison section exists specifically to answer "would something simpler have worked just as well?" See proposal.md - Why / What Changes.

## Goals / Non-Goals

**Goals:**
- Measure Baseline A (context-only, no memory) and Baseline B (naive vector memory, no contradiction handling) on the same 50 scenarios, using the same grading logic as the proposed system.
- Reuse the proposed system's *already-measured* canonical results from `evaluation-harness` rather than re-running it a third time - it hasn't changed, so re-running it would just spend tokens to reproduce a number we already have honestly.
- Keep the baselines as small, isolated, throwaway comparison code - not alternate production paths that need to be maintained going forward.

**Non-Goals:**
- Changing the proposed system.
- A fourth "hybrid-lite" baseline or any other variant - PLANNING.md names exactly two baselines, that's the scope.

## Decisions

**Baseline A has no `MemoryStore` at all - not an empty one, none.** Its `handle_message` builds messages from persona + all-turns-so-far-in-this-scenario + current message, and calls the LLM directly. This matches PLANNING.md's "Conversation context only. No persistent memory." literally, and trivially satisfies "no memory record of any kind is created" without needing a special-case check.

**Baseline B reuses the proposed system's own `MemoryExtractor`, `MemoryRetriever`, and `build_messages` - the only thing withheld is the resolver.** Extraction and embedding-based retrieval are not what PLANNING.md's Baseline Comparison is testing; the resolver (contradiction/duplicate/independent classification, status transitions) is the specific thing being isolated. Calling the existing `extract_and_store(..., resolver=None)` (already an optional parameter) means every SAVE candidate lands as a new ACTIVE row forever - exactly "naive vector memory" as PLANNING.md describes it - without writing a second extraction/retrieval implementation to maintain. Alternative considered: a fully independent Baseline B implementation - rejected, it would let extraction-quality differences (not the resolver) leak into the comparison and would double the surface area to keep correct.

**`run_scenario` takes an optional `engine_factory` callable, defaulting to the proposed system's factory.** This is a backward-compatible generalization: existing `evaluation-harness` call sites (`evaluate_scenario`, `run_eval.py`) keep working unchanged because they don't pass a factory. A factory is just `(llm, embedder, store) -> object-with-handle_message`; Baseline A's factory ignores the `store` argument (it doesn't use one), which is fine - the contract is "you get a fresh isolated store if you want it," not "you must use it."

**The comparison run reuses the proposed system's canonical `evaluation-harness` results instead of re-running it.** That run is already real, already measured, and the proposed system hasn't changed since - re-running it a third time would spend tokens to reproduce a number we can just read from `eval/results/run-20260902T044829Z.json`. Only Baseline A and Baseline B are run fresh. This is disclosed in the comparison report's methodology note, not silently done - "how was this number obtained" should never require guessing.

**Baseline runs are budgeted across separate API keys/sessions if needed, given the free-tier daily token cap already hit twice during `evaluation-harness`.** Baseline A is cheap (one LLM call per turn, no extraction); Baseline B is comparable to the proposed system minus resolver calls. If a key's quota is exhausted mid-run, the same recovery approach from `evaluation-harness` applies: switch keys, and if a run completes cleanly, use its real recorded results - never patch over a rate-limit-contaminated run's numbers.

## Risks / Trade-offs

- [Baselines might score close to the proposed system on categories that don't stress contradiction/history, making the comparison look unimpressive there] → Expected and fine: PLANNING.md's own logic is that FACTUAL_RECALL and LONG_RANGE_RECALL don't require contradiction handling, so baselines plausibly do fine there. The comparison is meaningful precisely where CONTRADICTION_UPDATE and TEMPORAL_REASONING are concerned - report all categories honestly regardless of which story the numbers tell.
- [Baseline B's unbounded memory growth (nothing ever superseded) could make retrieval noisier as more facts accumulate across a scenario's turns] → This is the point, not a bug to fix - it is exactly the naive behavior PLANNING.md wants measured.
- [Running two more full 50-scenario suites risks hitting the same daily token cap] → Mitigated by reusing the proposed system's existing results (one third fewer live runs needed) and, if needed, spreading Baseline A/B across separate keys as already practiced in `evaluation-harness`.

## Open Questions

None - the two baselines and the reuse of existing proposed-system results are direct, settled scoping decisions above.
