## Context

`evaluation-harness` grades end-to-end conversational correctness only - a wrong final answer could stem from extraction, resolution, or retrieval, and the harness can't distinguish which. PLANNING.md's Evaluation Metrics section explicitly names extraction precision/recall as a separate, useful measurement. See proposal.md - Why / What Changes.

## Goals / Non-Goals

**Goals:**
- A labeled ground-truth set covering clear SAVE cases (including multi-fact messages), clear IGNORE cases, and PLANNING.md's own Memory Extraction examples verbatim.
- A real, live measurement (no mocked LLM) of the extractor's precision and recall against that set.
- Matching robust to relation-naming variation, so the metric measures "did it capture the right facts," not "did it guess my exact relation vocabulary."

**Non-Goals:**
- Improving the extractor's prompt or schema to raise the score - this change measures, it does not tune.
- A large labeled set matching the 50-scenario suite's size - this is a supplementary diagnostic metric (PLANNING.md's "optional but highly valuable" quantitative results), not the core evaluation; a smaller, carefully chosen set (around 20 cases) is proportionate.

## Decisions

**Matching is value-based (case-insensitive substring, either direction), not relation-based.** `memory-explainability-cli`'s live demo run already showed the extractor choosing different relation labels (`dating` vs `ex_partner`) for what's arguably the same real-world fact - penalizing precision/recall for relation-naming choices would measure prompt-following pedantry, not extraction quality. Matching on the extracted value is what PLANNING.md's own examples care about ("Pizza... favourite food" should be saved; "eating pizza right now" should not) - the fact's content, not its label.

**Ground truth lives in `eval/scenarios/extraction_cases.jsonl`, a new file, not folded into `scenarios.jsonl`.** The 50-scenario suite's records describe conversation turns and a final question; extraction ground truth describes a single message and its expected SAVE/IGNORE facts - different enough shapes that a shared schema would need optional fields for both directions. A separate file keeps each schema simple.

**The evaluator is a new module (`src/evaluation/extraction_metrics.py`), reusing `MemoryExtractor` directly rather than going through `ConversationEngine` or `run_scenario`.** Extraction is being measured in isolation here, not as part of a conversation - there's no context builder, no resolver, no chat reply to produce. Reusing the runner/scenario machinery would add irrelevant moving parts.

**Report format mirrors the existing `write_report` pattern (timestamped JSON under `eval/results/`, methodology note included) for consistency, but is its own small writer rather than a generalization of `write_report`** - the payload shape (TP/FP/FN counts, precision, recall, per-case detail) is different enough from `ScenarioResult`-based metrics that force-fitting it into the existing `Metrics`/`ScenarioResult` types would be more confusing than a parallel, equally simple writer.

## Risks / Trade-offs

- [Value-based substring matching can still let a wrong-but-superficially-similar value count as a match] → Accepted trade-off, same class as the deterministic scenario checks; per-case detail is included in the report so a suspicious match is visible on inspection, not hidden behind an aggregate number.
- [A ~20-case set is small enough that one or two misses swing the percentage noticeably] → Disclosed plainly when reporting the result (an actual count, e.g. "18/20", alongside the percentage) rather than presenting the percentage alone as if it were measured on a larger sample.

## Open Questions

None.
