## 1. Scenario Schema and Loader

- [x] 1.1 Define `ScenarioCategory` (FACTUAL_RECALL / LONG_RANGE_RECALL / CONTRADICTION_UPDATE / TEMPORAL_REASONING / PERSONA_CONSISTENCY) and a `Scenario` Pydantic model (id, category, turns: list[str], final_question, expected_substring: str | None, persona_expectation: str | None) with validation that deterministic categories require `expected_substring` and PERSONA_CONSISTENCY requires `persona_expectation`, and verify a unit test rejects a factual-category scenario missing `expected_substring`
- [x] 1.2 Implement `load_scenarios(path) -> list[Scenario]` reading `eval/scenarios/scenarios.jsonl`, and verify a unit test loads a small fixture JSONL file into the expected `Scenario` objects

## 2. Scenario Dataset Content

- [x] 2.1 Author 10 factual recall scenarios (single fact stated, then asked back, per PLANNING.md's Example Evaluation Cases) into `eval/scenarios/scenarios.jsonl`
- [x] 2.2 Author 10 long-range recall scenarios (fact stated early, multiple unrelated turns in between, then asked late) into the same file
- [x] 2.3 Author 10 contradiction/update scenarios (a fact stated, then contradicted/updated, then asked for current truth) into the same file
- [x] 2.4 Author 10 temporal reasoning scenarios (mirroring the contradiction/update pairs but asking for the historical fact instead of current truth) into the same file
- [x] 2.5 Author 10 persona consistency scenarios (questions likely to tempt drift into generic assistant language or contradict a defined persona trait, per PLANNING.md's Persona Drift Detection examples) into the same file
- [x] 2.6 Verify with `load_scenarios`: the file parses without error and contains at least 10 scenarios in each of the 5 categories (50 total)

## 3. Eval Runner: Scenario Execution

- [ ] 3.1 Implement `run_scenario(scenario, llm, embedder) -> tuple[response, engine]`: builds a fresh `MemoryStore(":memory:")` and `ConversationEngine`, sends each of the scenario's `turns` through `handle_message` in order, then sends `final_question` and returns its response, and verify a unit test (mocked LLM) confirms turns are sent in order before the final question
- [ ] 3.2 Verify store isolation: running two scenarios in sequence with the same LLM/embedder instances confirms the second scenario's store contains no memories from the first (unit test)

## 4. Eval Runner: Verdicts

- [ ] 4.1 Implement the deterministic check: for FACTUAL_RECALL / LONG_RANGE_RECALL / CONTRADICTION_UPDATE / TEMPORAL_REASONING scenarios, verdict is PASS if `expected_substring.lower()` is in the response (case-insensitive), else FAIL, and verify unit tests for both cases
- [ ] 4.2 Define `PersonaJudgment` (verdict: PASS/FAIL/PARTIAL, reasoning: str) and write the judge prompt (given persona traits + the scenario's `persona_expectation` + the actual response, classify consistency), and implement the judge call using the LLM provider, and verify a unit test with a mocked LLM response parses a valid judgment
- [ ] 4.3 Wire verdict selection: PERSONA_CONSISTENCY scenarios use the LLM judge, all other categories use the deterministic check, and verify a unit test confirms the correct check is used per category
- [ ] 4.4 Implement `ScenarioResult` (scenario_id, category, verdict, response, expected, reasoning: str | None) and produce one per executed scenario, and verify a unit test confirms all fields are populated, with `reasoning` set only for judged scenarios

## 5. Metrics and Reporting

- [ ] 5.1 Implement metrics aggregation: per-category and overall `pass_rate`, `partial_rate`, `fail_rate` computed strictly from the list of `ScenarioResult`s, and verify a unit test with a small fixed set of results produces the expected rates
- [ ] 5.2 Implement report writing: a JSON file under `eval/results/` per run (timestamped filename) containing the computed metrics, the full list of scenario results, and a short methodology note documenting the LLM-judge limitations, and verify a unit test confirms the written file round-trips (contains the same metrics and result count that were passed in)
- [ ] 5.3 Verify failure detail is present for every non-PASS scenario in the written report (unit test with a mix of PASS/FAIL/PARTIAL results)

## 6. Entry Point and Full Live Run

- [ ] 6.1 Add `src/evaluation/run_eval.py` with a `main()` that loads scenarios, runs them all against the real Groq/fastembed providers, computes metrics, writes the report, and prints a summary to stdout, runnable via `python -m src.evaluation.run_eval`
- [ ] 6.2 Run the full 50-scenario suite live and inspect the results: confirm the report was written, spot-check at least one PASS and (if any occur) one FAIL/PARTIAL per category against their actual responses, and record the genuinely measured overall pass rate (no fabricated numbers)
- [ ] 6.3 Based on the live run's actual failures (if any), write a brief failure-analysis note (which scenarios failed and why, in plain terms) to inform the README's eventual "known limitations" section - do not paper over real failures
