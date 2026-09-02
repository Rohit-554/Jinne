## Context

`ConversationEngine` currently exposes only `handle_message`; its store and retriever are private. The CLI loop recognizes only `/exit`. This change adds two read-only commands without changing turn-handling behavior. Depends on `memory-decay-and-reranking`'s `MemoryRetriever.retrieve_scored`. See proposal.md - Why / What Changes.

## Goals / Non-Goals

**Goals:**
- `/memories` (alias `/memory-timeline`): group stored memories and show lifecycle chains, matching PLANNING.md's Memory Timeline example.
- `/memory-debug`: show the score breakdown for what was actually retrieved on the last real turn, matching PLANNING.md's Explainability example.
- Keep both commands read-only and outside the normal turn/extraction pipeline.

**Non-Goals:**
- Any interactive drill-down, pagination, or filtering UI for these commands - plain stdout text output, consistent with CLAUDE.md's "do not build a large CLI framework."
- Changing what gets retrieved or how it's scored - this change only surfaces `memory-decay-and-reranking`'s existing `retrieve_scored` output.

## Decisions

**`/memory-debug` shows the last real turn's retrieval, not a fresh ad hoc query.** PLANNING.md's own example presents debug output as "which memories were retrieved and why" for something the user just asked - re-running retrieval against a synthetic query would show something the conversation didn't actually use. `ConversationEngine.handle_message` is changed to call `retriever.retrieve_scored` (instead of `retrieve`) and cache the result on `self._last_scored_memories`; the plain `Memory` list used for context building is derived from that same scored list, so this is not an extra retrieval call, just capturing what was already computed. A new `get_last_retrieval_debug() -> list[ScoredMemory]` getter exposes it (empty before any turn has run).

**`/memories` groups by memory type, not by relation, matching PLANNING.md's Memory Timeline example format exactly** (a `CAREER` heading with chronological entries under it, each showing value and status). A new `list_all_memories() -> list[Memory]` getter on `ConversationEngine` returns every memory regardless of status (unlike `retrieve`, which is ACTIVE-only) since the timeline's entire point is showing SUPERSEDED history alongside current ACTIVE state.

**Rendering lives in a new `src/cli/memory_commands.py`, not inside `ConversationEngine` or `MemoryRetriever`.** These are presentation functions (turning domain data into CLI text) with no business logic of their own - keeping them in the CLI layer matches the existing separation where `src/persona/render.py` and `src/chat/context_builder.py` do the same kind of formatting job for their own layers.

**The CLI loop checks for `/memories`, `/memory-timeline`, and `/memory-debug` before the normal `handle_message` call, the same way it already special-cases `/exit`.** No new command-parsing framework - a small set of `if` checks, consistent with CLAUDE.md's "do not build a large CLI framework."

## Risks / Trade-offs

- [`/memory-debug` before any turn has run has nothing to show] → `get_last_retrieval_debug()` returns an empty list; the render function shows a plain "no retrieval has happened yet" message rather than erroring.
- [Grouping by type in `/memories` can put unrelated relations under the same heading (e.g. two different CAREER relations)] → Matches PLANNING.md's own example exactly; acceptable for a prototype's timeline view, and each entry still shows its own value/status so nothing is hidden, just grouped coarser than by-relation would be.

## Open Questions

None.
