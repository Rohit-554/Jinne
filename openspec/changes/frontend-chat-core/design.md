## Context

`ConversationEngine.handle_message` is synchronous end-to-end (one `llm.complete()` call, full string back) and is already used by the CLI and the evaluation harness. FRONTENDPLAN.md's P0 explicitly wants streaming. This change adds an HTTP/streaming layer without changing that existing method or its callers. See proposal.md - Why / What Changes.

## Goals / Non-Goals

**Goals:**
- Real token-level streaming (Groq's SDK supports it), not a UI-side fake typing effect over an already-complete string.
- Reuse `ConversationEngine`'s existing retrieval/context-building/extraction logic for the streaming path - no parallel reimplementation.
- Turn metadata (retrieved/created/updated memories) derived from data the engine already produces, not new bookkeeping bolted on ad hoc.
- A dark chat UI a reviewer can actually use to talk to the real backend, plus a minimal memories list - nothing from FRONTENDPLAN.md's P1-P3.

**Non-Goals:**
- The retrieval-score inspector, memory timeline, persona panel, evaluation dashboard, baseline comparison, architecture page, demo seeding, animation/responsive polish - all explicitly later phases in FRONTENDPLAN.md's own priority list.
- Authentication, multi-user support, or production deployment concerns - out of scope for the whole project per CLAUDE.md.
- Changing `LLMProvider.complete()`'s existing contract or any existing caller (CLI, evaluation harness) - they keep working exactly as they do today.

## Decisions

**Streaming is a new, separate `StreamingLLMProvider` protocol (`complete_stream(messages) -> Iterator[str]`), not an addition to the existing `LLMProvider` protocol.** Extending the base protocol would force every existing fake/test double across the current test suite to grow a method they don't need, for a capability only the API layer uses. `GroqProvider` implements both `complete()` (unchanged) and the new `complete_stream()` (Groq's SDK's `stream=True` mode). Alternative considered: make streaming the only mode and have `complete()` just join the chunks - rejected, unnecessary churn to a method with many existing callers and tests that have nothing to do with this change.

**`ConversationEngine` gains a new `handle_message_stream(user_message) -> Iterator[str]` method, reusing everything else `handle_message` already does.** It does the same retrieval, historical retrieval, and context building, calls `llm.complete_stream(messages)` instead of `complete(messages)`, yields each chunk to the caller, accumulates the full response, and then runs the exact same recent-turns bookkeeping and `extract_and_store` call `handle_message` does. `handle_message` itself is untouched - the CLI and evaluation harness keep calling it exactly as before. Requires the injected `llm` to support `complete_stream`; called with a non-streaming provider, it raises a clear error rather than silently falling back to something that isn't actually streaming.

**Turn memory metadata is derived from data the engine already has, not new state.** `extract_and_store`'s return value (the list of newly-saved `Memory` rows) already tells us "created memories" for the turn. For "updated (superseded) memories," each created memory's own `supersedes_memory_id` field (already set by the resolver when it supersedes something) tells us exactly which existing memory to look up via `store.get(id)` - no new tracking needed anywhere in the resolver or store. `ConversationEngine` caches this turn's created-memories list the same way it already caches `_last_scored_memories` for `/memory-debug`.

**The API is a FastAPI app (`src/api/`) with one shared `ConversationEngine` instance per process, built at startup against the same `MemoryStore` file the CLI uses.** Matches how the CLI keeps one engine per process; a per-request engine would mean no memory persists across requests within a session, which defeats the purpose. `POST /api/chat` returns a `text/event-stream` response: response-text chunks as they arrive, then a final named SSE event carrying the turn's JSON metadata (retrieved/created/updated memory summaries) - SSE's multi-event-per-response support is exactly built for this shape, and it's a plain HTTP response the browser's native `EventSource`/`fetch` + `ReadableStream` can consume without a WebSocket handshake. `GET /api/memories` is a plain JSON REST endpoint (no streaming needed for a list). CORS is enabled for the local Vite dev origin only.

**The frontend is a separate Vite + React + TypeScript + Tailwind project under `frontend/`, not folded into the Python `src/` tree.** Matches FRONTENDPLAN.md's own suggested structure and keeps the two toolchains (Python/pytest, Node/npm) independent - CLAUDE.md's repo-structure conventions govern `src/`; `frontend/` is new, sibling territory with its own `package.json`.

**This change builds exactly FRONTENDPLAN.md's P0 slice of components**: `ChatPage`, a message list, `MessageInput`, streaming response rendering, and one minimal collapsible memories panel (a plain list of active memories - no `MemoryCard`/`MemoryStatusBadge`/tabs/timeline yet, those are named P1 in FRONTENDPLAN.md's own priority list). TanStack Query fetches the memories list (matching FRONTENDPLAN.md's state-management recommendation); the chat stream is handled with a plain `fetch` + `ReadableStream` reader, since SSE-per-message doesn't fit TanStack Query's cache-and-refetch model well.

## Risks / Trade-offs

- [Groq's streaming API could behave differently under load/rate-limiting than the non-streaming path already exercised] → Same provider, same account limits already documented as a real constraint (see `eval/FAILURE_ANALYSIS.md`'s Groq rate-limit history) - not a new risk, just a new code path hitting the same known limit.
- [SSE's final-event-carries-metadata pattern is slightly unusual to consume correctly on the frontend] → Documented in the API contract in tasks.md; a fetch+ReadableStream implementation with a small SSE line-parser is a well-understood pattern, not a novel one.
- [Introducing a second toolchain (Node/npm) alongside the Python project's established, well-tested workflow] → Deliberate and named in FRONTENDPLAN.md itself; kept strictly isolated to `frontend/`, no changes to how the Python side is built, tested, or run.

## Open Questions

None - P1-P3 scope is explicitly deferred (a scoping decision recorded above), not an open question.
