## Why

PLANNING.md's Retrieval Strategy section explicitly says "Do not use embedding similarity alone" and specifies a hybrid ranking combining semantic similarity with importance, recency, and confidence - the retriever currently ranks by cosine similarity only. PLANNING.md's Memory Decay section separately says "not all memories deserve equal permanence" and that decay should reduce retrieval priority for time-bound/temporary facts without deleting them. Both are named P3 differentiators that the retriever needs before the explainability commands (`/memory-debug`, `/memory-timeline`) can show a meaningful score breakdown.

## What Changes

- Replace `MemoryRetriever`'s pure-cosine-similarity ranking with a hybrid score combining semantic similarity, importance, confidence, and a recency/decay factor.
- Add per-memory-type decay half-lives (e.g. TEMPORARY_STATE decays over roughly a day, IDENTITY/RELATIONSHIP barely decays at all), applied as an exponential recency weight - decay reduces a memory's ranking contribution, it never changes stored status or deletes anything.
- Add a `retrieve_scored` method returning the full per-memory score breakdown (semantic similarity, importance weight, recency weight, confidence weight, final score) alongside the existing `retrieve`/`retrieve_historical` methods (which keep their current signatures and return types, now hybrid-ranked instead of similarity-only-ranked), laying groundwork for the `/memory-debug` command in a later change without building that CLI command here.

Out of scope: the `/memory-debug` and `/memory-timeline` CLI commands themselves (next phase); any change to the resolver, extraction, or persona logic.

## Capabilities

### Modified Capabilities
- `memory/memory-retrieval`: retrieval ranking becomes a hybrid score (semantic similarity + importance + confidence + recency/decay) instead of semantic similarity alone, and gains a scored-retrieval operation exposing the breakdown.

## Impact

- `MemoryRetriever.retrieve`/`retrieve_historical` change ranking order (same call signature and return type) for any existing caller (`ConversationEngine`, `BaselineBEngine`, the eval runner) - no call-site changes needed.
- No new dependencies; decay is a pure function of a memory's `type` and age, computed in Python.
