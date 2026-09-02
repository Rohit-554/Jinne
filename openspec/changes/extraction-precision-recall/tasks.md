## 1. Ground Truth Dataset

- [ ] 1.1 Define `ExtractionCase` (id, message, expected: list of `{relation, value}`, empty list for IGNORE cases) as a Pydantic model with a `load_extraction_cases(path) -> list[ExtractionCase]` JSONL loader, mirroring `scenarios.py`'s pattern, and verify a unit test loads a small fixture file
- [ ] 1.2 Author `eval/scenarios/extraction_cases.jsonl` with ~20 cases: PLANNING.md's own examples verbatim (pizza SAVE/IGNORE pair, Microsoft+Android-engineer multi-fact message), several more clear SAVE cases across different memory types, several more clear IGNORE cases (greetings, trivial immediate state), and at least one genuine multi-fact message beyond the PLANNING example
- [ ] 1.3 Verify the dataset loads without error and has at least 20 cases, with both SAVE (non-empty expected) and IGNORE (empty expected) cases represented

## 2. Matching and Metrics

- [ ] 2.1 Implement `values_match(a: str, b: str) -> bool` (case-insensitive substring match in either direction) and verify unit tests for an exact match, a substring match, and a non-match
- [ ] 2.2 Implement `score_case(case: ExtractionCase, actual_candidates: list[MemoryCandidate]) -> CaseScore` (true_positives, false_positives, false_negatives as lists of values) matching only SAVE-decision candidates against `case.expected` via `values_match`, and verify unit tests for: exact match (no FP/FN), a missed expected fact (FN), an unexpected extra candidate (FP), and a correctly-empty IGNORE case (no FP/FN when the extractor also produces no SAVE candidates)
- [ ] 2.3 Implement precision/recall aggregation across a list of `CaseScore`s (`TP/(TP+FP)`, `TP/(TP+FN)`, with total counts included), and verify a unit test with a small fixed set of case scores produces the expected precision and recall

## 3. Live Evaluator and Report

- [ ] 3.1 Implement `run_extraction_metrics(cases, llm) -> list[CaseScore]` calling the real `MemoryExtractor` for each case, and `write_extraction_report(case_scores, results_dir) -> Path` writing a timestamped JSON with aggregate precision/recall/counts, a methodology note, and full per-case detail (message, expected, actual, TP/FP/FN)
- [ ] 3.2 Add a runnable entry point (`python -m src.evaluation.run_extraction_eval`) loading the dataset, running it against the real Groq provider, writing the report, and printing a summary
- [ ] 3.3 Run it live against all ~20 cases and record the genuinely measured precision and recall
- [ ] 3.4 Add the real result to `eval/FAILURE_ANALYSIS.md` (or a new short note) and to `README.md`'s evaluation results section, including any misses found, in plain terms - no invented numbers
- [ ] 3.5 Run the full pytest suite and confirm nothing regressed
