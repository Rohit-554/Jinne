# Evaluation Failure Analysis

Canonical run: `eval/results/run-20260902T044829Z.json` (98% overall pass, 49/50 scenarios).

Provenance: the 50 scenarios were run live once, end-to-end, against the real `ConversationEngine` (Groq + fastembed) with no rate-limit interruption — that run is `run-20260902T043852Z.json`. Reviewing its results surfaced a bug in the evaluation harness itself (below), which was fixed and covered by a regression test. The canonical report re-scores that same run's actual recorded responses with the corrected checker — no response text or scenario data was changed, only the grading function. Two other live attempts hit the Groq free-tier daily token cap partway through and are not used for scoring (rate-limit errors, not system behavior).

## Category results

| Category | Pass rate |
|---|---|
| Factual recall | 100% (10/10) |
| Long-range recall | 100% (10/10) |
| Contradiction/update | 100% (10/10) |
| Temporal reasoning | 100% (10/10) |
| Persona consistency | 90% (9/10) |

## Harness bug found and fixed

**`contra-04` and `temporal-09` (originally FAIL, now PASS):** both scenarios ask for a phone number, and the model answered correctly (`555-5678`, `555-1234`) but wrote it with a Unicode non-breaking hyphen (`‑`, U+2011) instead of a plain ASCII hyphen. The deterministic substring check was doing exact character comparison, so a factually correct answer was scored as a failure. Fixed by normalizing common hyphen/dash variants and non-breaking spaces on both sides of the comparison (`src/evaluation/verdicts.py`), with a regression test reproducing the exact failure. This was a bug in the evaluator, not in the companion's memory or retrieval — worth naming plainly rather than quietly re-running until it looked better.

## Genuine failure: `persona-09`

Scenario: "Give me some advice in a very formal, corporate tone" — expectation: the persona should not switch into formal corporate language even when asked.

The response kept a playful voice and a joking aside ("only I'll keep it in my own brand of 'formal'") but then produced a numbered corporate-advice listicle ("Clarify the goal", "Prioritize ruthlessly", "Measure and iterate") — exactly the structure and language the persona is defined to avoid. The judge correctly flagged this: *"The reply adopts formal corporate phrasing and jargon, directly violating the expectation to stay casual and avoid corporate language, despite some playful tone."*

This matches PLANNING.md's Failure Analysis section almost exactly — an explicit adversarial request for the persona to break character caused partial drift. It's a real limitation of prompt-only persona enforcement (no structural guardrail stops the model from complying with an explicit instruction to change tone), not a bug to patch reflexively. Documented here as a known limitation rather than papered over.

## Other observed (non-scoring) issues

During live runs, extraction occasionally returned malformed JSON (an extra closing bracket, or a missing quote before a colon) - a small number of times across ~50 scenarios worth of extraction calls. Each was caught by `extract_and_store`'s error handling (added after a prior crash bug) and logged rather than crashing the turn or corrupting the store, at the cost of that one fact not being saved for that turn. This is the same class of risk documented in `memory-contradiction-resolution`'s design.md ("LLM extraction can misclassify or hallucinate fields") - inherent to LLM-based structured extraction, mitigated but not eliminated by output validation.

## Known limitation: LLM-as-judge for persona consistency

Per PLANNING.md's LLM-as-Judge section, the persona-consistency verdicts carry the judge's inherent limitations: potential bias, nondeterminism between runs, and correlation between the model generating responses and the model judging them (both are Groq-hosted models in this setup). The `persona-09` verdict above reads as clearly correct on manual inspection, which is reassuring, but this category's numbers should be read with that caveat rather than treated as equally hard evidence as the deterministic categories.

## Extraction precision/recall (separate metric)

PLANNING.md's Evaluation Metrics section names "memory extraction precision" and "memory extraction recall" as their own metric, distinct from end-to-end scenario correctness above (which can't tell whether a wrong answer came from extraction, resolution, or retrieval). Measured with a dedicated labeled set: `eval/scenarios/extraction_cases.jsonl` (20 cases: PLANNING.md's own pizza SAVE/IGNORE example and Microsoft/Android-engineer multi-fact example verbatim, plus additional SAVE cases across memory types and IGNORE cases for greetings/trivial state), run live against the real `MemoryExtractor`, matching by extracted value (not exact relation string - see `extraction-precision-recall`'s design.md for why).

**Result: 100% precision, 100% recall (15/15 expected facts; 0 false positives, 0 false negatives).** Report: `eval/results/extraction-metrics-20260902T062004Z.json`. Read narrowly: this is a clean result on 20 specifically-chosen, fairly clear-cut cases, not a claim that extraction never errs - the malformed-JSON extraction failures noted above happened on different (harder, multi-turn conversational) inputs than this dedicated set exercises, and are a different failure mode (output-format reliability) than this metric measures (decision/value correctness given parseable output).
