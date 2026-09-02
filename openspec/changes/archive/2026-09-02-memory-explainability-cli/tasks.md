## 1. ConversationEngine Accessors

- [x] 1.1 Change `ConversationEngine.handle_message` to call `retriever.retrieve_scored` instead of `retrieve`, derive the plain `Memory` list for context building from the scored results, and cache the scored results on `self._last_scored_memories`
- [x] 1.2 Add `ConversationEngine.get_last_retrieval_debug() -> list[ScoredMemory]` returning the cached scored results (empty list before any turn has run)
- [x] 1.3 Add `ConversationEngine.list_all_memories() -> list[Memory]` returning every stored memory regardless of status

## 2. Rendering

- [x] 2.1 Implement `render_memory_timeline(memories: list[Memory]) -> str` in `src/cli/memory_commands.py`, grouping by memory type and listing each entry's value and status in chronological order by `valid_from`, matching PLANNING.md's Memory Timeline example format
- [x] 2.2 Implement `render_memory_debug(scored: list[ScoredMemory]) -> str`, listing each memory's value with its semantic similarity, importance, recency, and final score, matching PLANNING.md's Explainability example format, and rendering a plain "no retrieval yet" message when the list is empty

## 3. CLI Wiring

- [x] 3.1 Recognize `/memories` and `/memory-timeline` in the CLI loop (`src/cli/main.py`), printing `render_memory_timeline(engine.list_all_memories())` and continuing the loop without calling `handle_message`
- [x] 3.2 Recognize `/memory-debug` the same way, printing `render_memory_debug(engine.get_last_retrieval_debug())`

## 4. Tests (written now, run later)

- [x] 4.1 Unit test: `get_last_retrieval_debug()` is empty before any turn, and populated with the same memories used in that turn's context after `handle_message` runs
- [x] 4.2 Unit test: `list_all_memories()` returns memories of every status, not just ACTIVE
- [x] 4.3 Unit tests for `render_memory_timeline`: groups by type, shows both a SUPERSEDED and its superseding ACTIVE entry under the same heading, and handles an empty memory list without erroring
- [x] 4.4 Unit tests for `render_memory_debug`: renders all four score components per entry, and shows a plain message for an empty list
- [x] 4.5 Unit tests (fake engine): the CLI loop handles `/memories` and `/memory-debug` without calling the engine's `handle_message`, and continues the loop afterward

All 16 tests verified passing in the final testing pass. Live-verified via the demo script (session 2): `/memories` correctly rendered the CAREER supersede chain (Stripe SUPERSEDED, OpenAI ACTIVE) alongside GOAL/RELATIONSHIP/TEMPORARY_STATE groups, and `/memory-debug` showed a sensible five-entry score breakdown for the preceding turn. The live run also surfaced a real, separate finding (duplicate-meaning memories under different relation labels, e.g. `dating`/`ex_partner`) - documented in README.md's Known Limitations rather than patched here, since it's a resolver-matching architecture question outside this change's scope.
