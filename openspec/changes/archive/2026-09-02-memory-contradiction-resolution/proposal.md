## Why

Right now every SAVE candidate from extraction is inserted as a brand-new ACTIVE memory, so telling the companion "I left Google and joined Microsoft" produces two contradictory ACTIVE `works_at` memories instead of one current truth and one preserved history. Per PLANNING.md's Contradiction Handling section, this is a major part of the assignment and the natural next step after the P0 core loop: without it there is no update/supersede behavior and no way to answer "where did I work before?"

## What Changes

- Add a `MemoryResolver` that, given a new SAVE candidate, looks at existing ACTIVE memories with the same subject+relation (or a strongly matching semantic duplicate) and classifies it as: a duplicate (skip), an update/contradiction (supersede the old memory, insert the new one as ACTIVE), a new independent fact (insert as ACTIVE, unrelated to anything existing), or an expression of uncertainty (insert as UNCERTAIN rather than ACTIVE).
- Add `MemoryStore` support for transitioning an existing memory's status (e.g. ACTIVE → SUPERSEDED) and setting `valid_until`, without deleting the row — supersede is a status transition, not a delete-and-reinsert.
- Route extraction's SAVE candidates through the resolver instead of directly into `MemoryStore.save`, in both `extract_and_store` and the `ConversationEngine`.
- Add historical retrieval: a way to find relevant SUPERSEDED memories (not just ACTIVE ones) so questions like "Where did I work before Microsoft?" can be answered, with the context builder labeling historical memories separately from current ones so the model doesn't confuse past truth with present truth.

Out of scope for this change: memory decay/EXPIRED handling (P3), hybrid retrieval reranking (P3), persona-consistency evaluation (P2 — this change doesn't touch persona behavior), and the evaluation harness (P2).

## Capabilities

### New Capabilities
- `memory/memory-resolver`: Classifies each SAVE candidate against existing ACTIVE memories (duplicate / update-contradiction / new fact / uncertain) and applies the resulting store transition.

### Modified Capabilities
- `memory/memory-store`: adds the ability to update an existing memory's lifecycle status and `valid_until` in place, so a record can move ACTIVE → SUPERSEDED without being deleted.
- `memory/memory-retrieval`: adds retrieval of relevant SUPERSEDED (historical) memories as a distinct operation from the existing ACTIVE-only retrieval.
- `chat/conversation-loop`: SAVE candidates now flow through the resolver rather than straight into the store, and the context assembled for the LLM includes relevant historical memories, labeled separately from current ones, when they are found.

## Impact

- Existing `extract_and_store` (memory/extractor) and `ConversationEngine` (chat) change how they persist SAVE candidates — no longer a blind insert.
- No new external dependencies; reuses the existing LLM and embedding provider interfaces.
- No breaking change to stored data (existing ACTIVE rows from the P0 change remain valid; the schema already has `status`, `valid_until`, and `supersedes_memory_id` columns, unused by data but present since the P0 schema).
