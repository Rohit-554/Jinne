## Why

FRONTENDPLAN.md's Goal is a presentation layer that makes the already-working memory architecture "easy to understand and impressive to demo" - explicitly not the core assignment, but built on top of it. FRONTENDPLAN.md itself is emphatic that frontend work should not start before "the backend core works reliably" (§29) - which it now does (P0-P6, 136 tests, live-demo-verified, real evaluation results). FRONTENDPLAN.md's own Implementation Priority names a P0 slice: Vite setup, dark theme, main chat, FastAPI connection, streaming, basic memory inspector. This change builds exactly that slice, nothing more.

## What Changes

- Add a FastAPI service (`src/api/`) that wraps the existing `ConversationEngine` and `MemoryStore` over HTTP for a browser client: a chat endpoint that streams the assistant's response and reports which memories were retrieved/created/updated for that turn (per FRONTENDPLAN.md's FastAPI Contract), and a basic endpoint listing current ACTIVE memories.
- Add a new `frontend/` Vite + React + TypeScript + Tailwind app: FRONTENDPLAN.md's dark palette and typography, a chat page (message history, streaming assistant responses, message input), and a minimal collapsible Memory Inspector panel listing currently active memories - no retrieval-score breakdown, timeline, persona panel, or evaluation dashboard yet.
- Wire the frontend to the FastAPI service for streaming chat and the basic memory list.

Out of scope (FRONTENDPLAN.md's own P1-P3, deferred to follow-up changes): the retrieval-score inspector, memory timeline UI, persona panel, evaluation dashboard, baseline comparison table, architecture page, demo-seeding mode, and animation/responsive polish.

## Capabilities

### New Capabilities
- `api/chat-service`: A FastAPI HTTP+streaming service exposing the existing conversation engine's chat turn and a basic active-memories list to an HTTP client, without changing the underlying engine's behavior.
- `frontend/chat-ui`: A dark-themed React chat interface (message history, streaming responses, input) with a minimal active-memories inspector panel, consuming `api/chat-service`.

## Impact

- New Python dependencies (FastAPI, an ASGI server) added to `pyproject.toml`; no change to `src/memory`, `src/chat`, `src/persona`, or `src/llm` behavior - the API is a new consumer of `ConversationEngine`, the same relationship the CLI and evaluation harness already have.
- New `frontend/` directory (a separate Node/npm project) alongside the existing Python `src/`.
- Running the frontend requires two processes: the FastAPI backend and the Vite dev server - documented once this change lands.
