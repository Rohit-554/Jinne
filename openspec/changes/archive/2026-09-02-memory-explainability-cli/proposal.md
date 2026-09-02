## Why

PLANNING.md's Explainability/Memory Debugger and Memory Timeline sections call these "an important differentiator" and "important for demonstrating and debugging" the system - CLAUDE.md's CLI Commands list already names `/memories`, `/memory-debug`, and `/memory-timeline` as intended commands, but the CLI currently only handles plain chat turns and `/exit`. Without these, the lifecycle work from `memory-contradiction-resolution` (supersede chains) and the scoring work from `memory-decay-and-reranking` (score breakdowns) are invisible to anyone using the CLI - they only show up as assertions in tests.

## What Changes

- Add a `/memories` command (aliased `/memory-timeline`) that prints stored memories grouped by relation, showing each one's lifecycle chain (e.g. a `works_at` group showing Google SUPERSEDED then Microsoft ACTIVE), matching PLANNING.md's Memory Timeline example format.
- Add a `/memory-debug` command that runs retrieval for the current conversation and prints each retrieved memory's score breakdown (semantic similarity, importance, recency, confidence, final score), using `MemoryRetriever.retrieve_scored` from `memory-decay-and-reranking`, matching PLANNING.md's Explainability example format.
- Wire both commands into the CLI's `run()` loop alongside the existing `/exit` handling.

Out of scope: any change to memory storage, extraction, resolution, or retrieval ranking logic itself - this change only adds read-only, presentational commands over data those systems already produce.

## Capabilities

### New Capabilities
- `cli/memory-commands`: `/memories` (timeline view of stored memories and their lifecycle chains) and `/memory-debug` (retrieval score breakdown for the current context), as CLI commands alongside normal chat turns.

## Impact

- `src/cli/main.py`'s `run()` loop recognizes two new command strings; no change to `ConversationEngine`'s `handle_message` contract.
- Depends on `memory-decay-and-reranking`'s `retrieve_scored` method for `/memory-debug`'s score breakdown.
