## Context

The P0 core loop (archived `companion-memory-core-loop`) always inserts a SAVE candidate as a brand-new ACTIVE memory. This is P1 per PLANNING.md's Implementation Priorities: contradiction detection, superseding, and temporal state. See proposal.md - Why / What Changes for motivation and scope.

## Goals / Non-Goals

**Goals:**
- Make "I left Google and joined Microsoft" produce one current truth (Microsoft, ACTIVE) and one preserved history (Google, SUPERSEDED), matching PLANNING.md's Contradiction Handling example.
- Answer historical questions ("Where did I work before Microsoft?") from SUPERSEDED memories, without ever presenting them as current.
- Avoid over-triggering supersede on relations that can legitimately hold multiple simultaneous values (e.g. liked languages), per PLANNING.md's "do not blindly append contradictory memories" alongside "do not delete historical facts unnecessarily."

**Non-Goals:**
- Memory decay / EXPIRED lifecycle handling (P3).
- Hybrid retrieval reranking combining importance/recency/status weights (P3) — historical retrieval reuses the existing plain cosine-similarity ranking from memory-retrieval, just against SUPERSEDED rows instead of ACTIVE ones.
- Persona-consistency evaluation (P2) — this change does not touch persona behavior.
- A full evaluation harness (P2).

## Decisions

**The resolver is an LLM-backed classifier, not a pure key-matcher.** A naive rule ("same subject+relation ⇒ always supersede") is wrong for relations that can hold multiple simultaneous values (liking both Kotlin and Python). PLANNING.md's Contradiction Handling section asks the resolver to judge duplicate / update / contradiction / new-independent-fact, which is a semantic judgment, not a string comparison. So: the resolver first does a cheap deterministic lookup (existing ACTIVE memories with the same subject+relation as the candidate) to find *candidates* to compare against, then — only when that lookup is non-empty — makes one LLM call classifying the relationship (DUPLICATE / SUPERSEDE / INDEPENDENT) against those candidates. When the lookup is empty, it skips the LLM call entirely and inserts as a new independent fact (no ambiguity to resolve, no cost to spend). Alternative considered: always call the LLM per candidate regardless of whether anything exists to compare against — rejected as wasted latency/cost for the common case of a genuinely new fact.

**Uncertainty is a deterministic confidence-threshold check, not another LLM call.** The extractor already outputs a `confidence` float per candidate (added in P0). Reusing it — "confidence below a configured threshold ⇒ store as UNCERTAIN" — is reproducible and needs no new extraction-schema field or extra provider call. Alternative considered: have the LLM explicitly flag "uncertain: true" during extraction — rejected as an unnecessary schema change when confidence already captures the same signal, and per CLAUDE.md's engineering principle to measure behavior with concrete, reproducible checks. The threshold is a module constant (not user-configurable via env in this change) so behavior stays predictable; making it tunable is a straightforward follow-up if it needs adjusting.

**Supersede is a status transition, not a delete-and-reinsert.** `MemoryStore` gains `update_status(memory_id, status, valid_until=None)` that mutates the existing row in place (status, valid_until, updated_at), preserving its id and all other historical fields. This matches PLANNING.md's "do not delete historical facts unnecessarily" and keeps `supersedes_memory_id` on the *new* row pointing at a still-resolvable old row. Alternative considered: mark old row somehow via a soft-delete flag distinct from `status` — rejected, `status` already models exactly this lifecycle (ACTIVE/SUPERSEDED/EXPIRED/UNCERTAIN per the P0 schema).

**Historical retrieval is a second method on the existing `MemoryRetriever`, not a new module.** `retrieve_historical(message, top_k)` reuses the same embedding + cosine-similarity machinery as `retrieve()`, just filtering `store.list(status=SUPERSEDED)` instead of `ACTIVE`. This keeps the "embeddings for relevance, structured status for truth" principle (PLANNING.md's Important Architectural Statement) intact: the only change is which status the structured filter selects. Alternative considered: a unified `retrieve(message, top_k, statuses=[...])` — rejected for this change; keeping two clearly-named methods keeps call sites explicit about "current" vs "historical" intent, matching how the context builder needs to label them separately anyway.

**The context builder gets an optional `historical_memories` parameter, rendered as a separate labeled section.** Mirrors PLANNING.md's Context Builder example ("Relevant historical memories if needed"). The system prompt explicitly instructs the model to treat the historical section as past-tense fact, never current state — this is a prompting decision, not a structural guarantee, and is exactly the kind of thing the eval harness (P2) should later test for drift.

**`ConversationEngine` decides whether to fetch historical memories via a lightweight heuristic**: call `retrieve_historical()` whenever `retrieve()`'s top ACTIVE result set is not already a strong match (or always, at a small `top_k` like 2, since the historical call is cheap — same embedding, no extra LLM call). Given the low cost, this change always calls `retrieve_historical(message, top_k=2)` alongside the existing ACTIVE retrieval and lets the prompt instruction (not a similarity-score gate) keep irrelevant historical memories from being volunteered by the model. Alternative considered: only fetch historical memories when the message contains hedge words like "before"/"used to" — rejected as brittle keyword matching that PLANNING.md explicitly asks to avoid ("infer relevance beyond exact keyword matching").

## Risks / Trade-offs

- [Resolver LLM call adds one extra provider round-trip per SAVE candidate that has a same-subject+relation match] → Acceptable for a prototype's turn latency; only triggered when there's genuine ambiguity to resolve, not on every message.
- [Confidence-threshold-based uncertainty detection may miscategorize borderline statements] → Documented as a known limitation; the threshold is a single named constant, easy to tune once real extraction data is observed. Not claimed as more accurate than it is.
- [Always fetching historical memories on every turn spends one extra embedding-similarity pass even when nothing historical is relevant] → Cheap (no LLM call, local embedding + in-memory cosine similarity over a small dataset); the prompt instruction, not a retrieval gate, is what keeps irrelevant history out of responses — a known soft guarantee, not a hard one.
- [LLM-based resolver classification can misjudge DUPLICATE vs SUPERSEDE vs INDEPENDENT, same class of risk as extraction] → Same mitigation as extraction: Pydantic validates the output shape; classification *quality* is left to be measured by the evaluation harness (P2), not solved here.

## Open Questions

None — remaining unknowns (exact certainty threshold value, whether historical retrieval should eventually gate on a similarity score) are tunable constants that don't change the specs or task breakdown, and are called out as risks above.
