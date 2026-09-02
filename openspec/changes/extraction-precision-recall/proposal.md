## Why

PLANNING.md's Evaluation Metrics section explicitly names "Memory extraction precision" and "Memory extraction recall" as metrics this project should measure. `evaluation-harness` measured end-to-end conversational correctness (does the final answer contain the right fact) but never isolated extraction quality itself - a wrong final answer could come from bad extraction, bad resolution, or bad retrieval, and the current harness can't tell which. This closes that gap with a real, measured number.

## What Changes

- Add a labeled extraction ground-truth dataset: messages paired with the SAVE candidates (relation+value) that should be extracted, or an empty expected set for messages that should be IGNOREd - covering PLANNING.md's own Memory Extraction examples plus additional SAVE/IGNORE/multi-fact cases.
- Add an extraction evaluator that runs the real `MemoryExtractor` (live LLM call, no mocks) against each case and matches actual SAVE candidates against expected ones (by relation+value, case-insensitive) to count true positives, false positives, and false negatives.
- Compute precision (`TP / (TP + FP)`) and recall (`TP / (TP + FN)`) across the dataset, reusing the existing reporting pattern (a written JSON report, real measured numbers only).
- Run it live and record the genuine result in the project's evaluation documentation.

Out of scope: changing the extractor itself to improve its score - this change measures extraction quality, it does not try to fix it.

## Capabilities

### New Capabilities
- `evaluation/extraction-metrics`: A labeled extraction ground-truth dataset and an evaluator that computes real precision/recall for the memory extractor, independent of end-to-end scenario grading.

## Impact

- New `eval/scenarios/extraction_cases.jsonl` and a new `src/evaluation/extraction_metrics.py`-family module; no change to `src/memory/extractor` itself.
- Makes real LLM calls (one per case) - a manual/on-demand command, same as the rest of `src/evaluation`.
