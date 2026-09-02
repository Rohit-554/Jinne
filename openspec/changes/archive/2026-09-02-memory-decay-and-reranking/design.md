## Context

`MemoryRetriever.retrieve`/`retrieve_historical` currently rank purely by cosine similarity over embeddings. PLANNING.md's Retrieval Strategy and Memory Decay sections ask for a hybrid score and type-based decay respectively; this change adds both to the retriever without touching extraction, resolution, or persona. See proposal.md - Why / What Changes.

## Goals / Non-Goals

**Goals:**
- Combine semantic similarity with importance, confidence, and a recency/decay factor into one ranking score.
- Make decay a per-memory-type rate (fast for TEMPORARY_STATE, effectively negligible for IDENTITY/RELATIONSHIP) applied only to ranking, never to stored data.
- Expose the full score breakdown via a new method, without changing `retrieve`/`retrieve_historical`'s existing signatures.

**Non-Goals:**
- `/memory-debug` or `/memory-timeline` CLI commands (next phase) - this change only makes the score breakdown available in code.
- Making weights configurable via environment variables - they are named module constants, consistent with `CERTAINTY_THRESHOLD` in the resolver.
- Entity-overlap scoring (PLANNING.md mentions it as a possible signal) - not implemented here; semantic similarity, importance, confidence, and recency are the four signals this change adds, matching what's cheaply computable from data already on the `Memory` model.

## Decisions

**Hybrid score is a weighted sum: `final_score = w_sim * similarity + w_imp * importance + w_conf * confidence + w_rec * recency_factor`, with fixed weights as named constants.** A weighted sum is the simplest combination that satisfies "not similarity alone" and is easy to explain in a score breakdown (each term is independently visible) - matching the explainability goal PLANNING.md's `/memory-debug` section describes. Alternative considered: a learned or rank-based combination - rejected as unnecessary complexity for a prototype with no training data to fit weights against.

**Recency factor is exponential decay per memory type: `0.5 ** (age_days / half_life_days)`.** Half-life is the standard, well-understood parameterization for "how fast does this become less relevant" and naturally produces a smooth 0-1 weight without a hard cutoff. Half-lives are a small `dict[MemoryType, float]` module constant: very short for `TEMPORARY_STATE`, medium for `EVENT`/`PLAN`, and long (multi-year, i.e. effectively non-decaying within a prototype's realistic timeframe) for `IDENTITY`/`RELATIONSHIP`/`PREFERENCE`/`CAREER`/`GOAL`/`PERSON`/`LOCATION`/`EXPERIENCE`/`OTHER`. Alternative considered: a single global half-life - rejected, PLANNING.md's Memory Decay section is explicit that decay factors include "memory type."

**Decay affects ranking only - it never touches `status`, `importance`, `confidence`, or any other stored field.** This matches PLANNING.md's "Decay does not necessarily mean deletion. It can simply reduce retrieval priority" and keeps decay entirely inside the retriever, with no new store-mutation surface (unlike the resolver's `update_status`, which is a real lifecycle transition).

**`retrieve_scored(message, top_k) -> list[ScoredMemory]` is a new method; `retrieve`/`retrieve_historical` keep their existing signatures and return `list[Memory]`, now internally ranked by the hybrid score instead of raw similarity.** This is the smallest change that satisfies both "expose the breakdown" and "don't break existing callers" - `ConversationEngine`, `BaselineBEngine`, and the eval runner all keep working unchanged, they just get better-ranked results.

## Risks / Trade-offs

- [Fixed weights are a guess, not tuned against real usage data] → Acceptable for a prototype; named constants make them easy to revisit, and the score breakdown this change adds is exactly what would be needed to tune them later.
- [Combining importance/confidence (0-1 scale) with cosine similarity (-1 to 1, typically 0-1 for real text) without normalization could let one signal dominate if weights aren't chosen carefully] → Mitigated by choosing weights so similarity remains the dominant term (matching PLANNING.md's framing that embeddings do the primary relevance filtering, with the other signals as tie-breaking/reranking adjustments), verified by the "higher importance can outrank slightly higher similarity" scenario in the spec, not by a full similarity-swamping.

## Open Questions

None - entity-overlap scoring is explicitly deferred (Non-Goals), and weight values are tunable constants, not a design fork.
