## Why

We need a working core loop before any of the memory-intelligence, evaluation, or differentiator work in PLANNING.md is possible: a CLI companion that persists structured memories to SQLite, extracts memory-worthy facts from what the user says, retrieves relevant memories semantically, and injects them into the LLM context. Until this loop exists and survives an application restart, none of the later contradiction handling, temporal reasoning, persona consistency, or evaluation harness work (PLANNING.md P1–P3) has anything to build on.

## What Changes

- Define the SQLite-backed memory schema (id, type, subject, relation, value, status, importance, confidence, timestamps, `supersedes_memory_id`, `source_message_id`) and a `MemoryStore` module for creating and reading memory records.
- Add an LLM-driven `MemoryExtractor` that inspects each user message and decides `SAVE` or `IGNORE` for zero or more candidate memories (no `UPDATE`/contradiction handling yet — that is a follow-up change).
- Add embedding-based `MemoryRetriever` candidate retrieval: embed stored memories and the current message, return the top-k most similar ACTIVE memories.
- Add a minimal static `Persona` definition (name, traits, communication style, stable preferences) loaded by the context builder.
- Add a `ConversationEngine` CLI loop: takes user input, retrieves relevant memories, builds a compact context (persona + relevant memories + recent turns + current message), calls the LLM behind a small provider interface, prints the response, and runs extraction + storage on the user message.
- Persist all memory across process restarts (SQLite file on disk) so a fact told in one session is recallable in a later session.

## Capabilities

### New Capabilities
- `memory/memory-store`: SQLite schema and CRUD access for structured memory records, including lifecycle `status` field (values defined, only `ACTIVE` produced by this change).
- `memory/memory-extraction`: LLM-based extraction of user messages into `SAVE` or `IGNORE` memory candidates, with a taxonomy of memory types.
- `memory/memory-retrieval`: Embedding generation and similarity-based candidate retrieval of ACTIVE memories relevant to the current message.
- `persona`: Static companion persona definition consumed by context construction.
- `chat/conversation-loop`: CLI conversation loop, LLM provider interface, context builder, and end-to-end wiring of persistence, extraction, and retrieval across restarts.

### Modified Capabilities
(none — this is the first change in the project)

## Impact

- New repo structure under `src/` (`chat/`, `persona/`, `memory/{extractor,store,retriever,models}/`, `llm/`, `cli/`) and `tests/` per CLAUDE.md's Repo Structure section.
- New SQLite database file (local, on disk) as the memory source of truth.
- New dependency on an LLM provider API (Groq, configurable via environment variables and swappable behind the provider interface) and a local embeddings model (fastembed) so no paid API key is required for retrieval.
- Out of scope for this change (left for follow-up changes per PLANNING.md P1–P3): contradiction/supersede resolution, temporal/historical queries, memory decay, hybrid reranking beyond basic similarity, `/memory-debug` and `/memory-timeline` commands, persona drift detection, and the evaluation harness.
