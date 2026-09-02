## 1. Decay and Scoring

- [x] 1.1 Define `DECAY_HALF_LIFE_DAYS: dict[MemoryType, float]` (short for TEMPORARY_STATE, medium for EVENT/PLAN, long for the rest) and a `recency_factor(memory, now) -> float` function computing `0.5 ** (age_days / half_life_days)`
- [x] 1.2 Define `ScoredMemory` (memory, semantic_similarity, importance_weight, recency_weight, confidence_weight, final_score) and a scoring function combining them into `final_score` with named weight constants

## 2. Retriever Integration

- [x] 2.1 Implement `MemoryRetriever.retrieve_scored(message, top_k) -> list[ScoredMemory]` for ACTIVE memories, ranked by `final_score` descending
- [x] 2.2 Update `retrieve()` and `retrieve_historical()` to rank via the hybrid score internally (via `retrieve_scored`-style logic) while keeping their existing `list[Memory]` return type and signature unchanged

## 3. Tests (written now, run later)

- [x] 3.1 Unit tests for `recency_factor`: a memory of a fast-decaying type at N half-lives old has roughly half the recency weight per half-life elapsed; a memory of a slow-decaying type barely decays over a realistic timeframe
- [x] 3.2 Unit test: two memories with similar similarity but a large importance gap rank with the higher-importance one at or above the other
- [x] 3.3 Unit test: `retrieve_scored` returns all five fields per candidate and `final_score` matches the weighted combination
- [x] 3.4 Unit tests: `retrieve()`/`retrieve_historical()` still respect status filtering and top_k bounding (same contract as before), now via the hybrid ranking

All 15 tests (tests/test_decay.py, tests/test_scoring.py, tests/test_memory_retrieval.py) verified passing in the final testing pass alongside the full project suite (118 passed) and a live CLI demo run.
