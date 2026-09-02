## Context

P0 (`companion-memory-core-loop`) and P1 (`memory-contradiction-resolution`) are implemented and manually verified, but "manually verified" is not what PLANNING.md asks for at P2: a repeatable scenario suite with measured pass rates. This change builds that suite, purely additive on top of the existing `ConversationEngine`/`MemoryStore`/providers. See proposal.md - Why / What Changes for motivation and scope.

## Goals / Non-Goals

**Goals:**
- Run ~50 real scenarios (10 per category: factual recall, long-range recall, contradiction/update, temporal reasoning, persona consistency) end-to-end through the actual `ConversationEngine`, not mocks, and report genuinely measured pass rates.
- Keep factual-category checks deterministic (substring match), reserving the LLM-judge for the one genuinely subjective category (persona consistency), per PLANNING.md's "use deterministic checks... where possible."
- Produce a durable, reviewable artifact per run (results file with per-scenario detail) so failures can be inspected individually, not just summarized away.

**Non-Goals:**
- Baseline comparison (PLANNING.md's Baseline A/B) - needs separate baseline system variants; left for a follow-up change.
- Any change to `src/memory`, `src/chat`, `src/persona`, `src/llm` behavior - this change is a consumer, not a modifier, of those modules.
- CI integration or scheduled runs - this is a manual/on-demand command per CLAUDE.md's CLI Commands section (`/eval` is listed as optional).

## Decisions

**Scenarios live in one `eval/scenarios/scenarios.jsonl` file, one JSON object per line.** JSONL per CLAUDE.md's Tech Stack ("Evaluation data: JSON / JSONL"). One file (not one file per category) keeps authoring and loading simple for ~50 records; the `category` field on each record is what categorizes them, not file location. Alternative considered: one file per category - rejected as unnecessary indirection for this size of dataset.

**Each scenario replays through a real `ConversationEngine` against an in-memory SQLite store (`:memory:`), not a temp file.** `MemoryStore`'s `db_path` is passed straight to SQLAlchemy's `sqlite:///` URL, and `:memory:` is a valid SQLite path for that - no temp-file cleanup needed, and each scenario gets a genuinely isolated store (a new engine/connection per `MemoryStore()` instance). The LLM and embedding provider instances are still shared/reused across scenarios (real network clients, and the embedding model is expensive to reload) - only the store and the `ConversationEngine` wrapping it are per-scenario.

**Deterministic categories check `expected_substring.lower() in response.lower()`.** Simple, reproducible, no LLM call needed for the four fact-based categories - matches PLANNING.md's preference for deterministic checks and avoids paying the "evaluator/generation model correlation" bias that using an LLM judge for everything would introduce. Alternative considered: LLM-judge every category for consistency - rejected, deterministic checks are strictly more trustworthy for these categories and PLANNING.md explicitly asks for them where possible.

**Persona consistency uses an LLM-as-judge returning PASS/FAIL/PARTIAL plus reasoning, following the same JSON-schema-and-parse pattern as the extractor and resolver** (`llm.complete()` + `parse_json_object` + Pydantic validation). Reusing the established pattern keeps this module consistent with the rest of the codebase rather than inventing a new parsing approach. Known limitations (judge bias, nondeterminism, evaluator/generation model correlation - same model family judging itself) are documented in the results report's methodology notes, per PLANNING.md's LLM-as-Judge section, not silently assumed away.

**PARTIAL is tracked as its own bucket, not folded into PASS or FAIL.** A pass rate that quietly counts PARTIAL as PASS would overstate results; counting it as FAIL would understate persona nuance the judge explicitly flagged. Reporting `pass_rate`, `partial_rate`, and `fail_rate` separately per category keeps the number honest, per CLAUDE.md's "never fabricate metrics" principle.

**Results are written as one JSON file per run under `eval/results/`** (already gitignored), containing computed metrics plus every scenario's full result record (id, category, verdict, response, expected outcome, judge reasoning where applicable). This is the artifact PLANNING.md's Failure Analysis and README's "actual results" section will draw from.

**Entry point is `python -m src.evaluation.run_eval`**, mirroring the existing `python -m src.cli` convention. No new CLI framework, per CLAUDE.md's Tech Stack.

## Risks / Trade-offs

- [A full 50-scenario run makes on the order of hundreds of real LLM calls (chat + extraction + occasional resolver calls per turn) and takes real wall-clock time] → Acceptable for a manual/on-demand evaluation command, not something run per-commit; documented as such in the README once written.
- [LLM-judge persona verdicts are themselves imperfect (the same class of unreliability as extraction/resolution)] → Documented as a named limitation in the report's methodology, per PLANNING.md's LLM-as-Judge section; not presented as ground truth.
- [Substring matching for deterministic categories can false-negative on a correct-but-differently-worded answer] → Accepted trade-off for reproducibility; scenario authoring should pick expected substrings the model is very likely to use verbatim (e.g. a specific name or place), and failures are logged with full response text so a false negative is visible on inspection, not silently lost.

## Open Questions

None - baseline comparison is explicitly deferred (not an open question, a scoping decision recorded above), and scenario count/category split follows PLANNING.md's stated targets directly.
