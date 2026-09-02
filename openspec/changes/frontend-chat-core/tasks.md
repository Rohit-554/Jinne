## 1. Streaming Provider and Engine Support

- [ ] 1.1 Define a `StreamingLLMProvider` protocol (`complete_stream(messages) -> Iterator[str]`) separate from the existing `LLMProvider`, and implement it on `GroqProvider` using Groq's SDK streaming mode, and verify a live smoke test yields more than one chunk that concatenate to a non-empty response
- [ ] 1.2 Add `ConversationEngine.handle_message_stream(user_message) -> Iterator[str]`, reusing the same retrieval/historical-retrieval/context-building as `handle_message`, calling `complete_stream` instead of `complete`, yielding chunks, then running the same recent-turns bookkeeping and `extract_and_store` call after the full response is assembled, and verify `handle_message`'s existing tests still pass unchanged
- [ ] 1.3 Cache the turn's newly-saved memories on the engine (from `extract_and_store`'s return value) and add `ConversationEngine.get_last_turn_memory_changes() -> tuple[list[Memory], list[Memory]]` returning (created, updated) where `updated` is derived by looking up each created memory's `supersedes_memory_id` via the store, and verify unit tests for: a turn with no memory changes returns two empty lists, and a turn that supersedes an existing memory returns it in `updated`

## 2. FastAPI Service

- [ ] 2.1 Add `src/api/app.py` with a FastAPI app constructing one shared `ConversationEngine` at startup against the configured `MemoryStore`, and CORS enabled for the local Vite dev origin
- [ ] 2.2 Add `POST /api/chat`: a `text/event-stream` response streaming `handle_message_stream`'s chunks, followed by a final named SSE event carrying the turn's JSON metadata (retrieved/created/updated memory summaries from `get_last_retrieval_debug`/`get_last_turn_memory_changes`), and verify a test client receives multiple chunks plus a well-formed final metadata event
- [ ] 2.3 Add `GET /api/memories`: returns all currently ACTIVE memories as JSON (excluding the `embedding` field), and verify a test confirms only ACTIVE memories are returned
- [ ] 2.4 Verify with a live `uvicorn` process and `curl`/an SSE-aware script: a real chat request streams real chunks from the real model and a real metadata event, and `/api/memories` returns real stored memories

## 3. Frontend Scaffold and Chat Page

- [ ] 3.1 Create the Vite + React + TypeScript app under `frontend/`, add Tailwind configured with FRONTENDPLAN.md's dark palette and typography, and verify `npm run build` succeeds
- [ ] 3.2 Build `ChatPage`: companion name + short persona description header, scrollable message history, `MessageInput` with send button, and verify the page renders in dev mode without console errors
- [ ] 3.3 Implement streaming response rendering: a `fetch` + `ReadableStream` SSE reader that appends response text incrementally to the in-progress assistant message as chunks arrive, and parses the final metadata event
- [ ] 3.4 Implement a minimal collapsible Memory Inspector panel: fetches `GET /api/memories` (via TanStack Query), lists each active memory's value, and shows a plain empty-state message when there are none
- [ ] 3.5 Wire the chat page to `POST /api/chat` end-to-end

## 4. End-to-End Verification

- [ ] 4.1 Run the FastAPI backend and Vite dev server together and verify live: sending a message streams a real response, the memories panel reflects a fact just mentioned after a refetch, and a contradiction (stated, then updated) is reflected in a subsequent `/api/memories` call
- [ ] 4.2 Run the full Python pytest suite and confirm nothing regressed
- [ ] 4.3 Note in the change's completion summary that automated interactive browser verification (e.g. Playwright) is not part of this environment's toolset - frontend verification here covers build success, dev-server rendering without console errors, and scripted API-contract checks (curl/SSE), not a fully automated click-through; a manual browser check by the user is the remaining gap and should be flagged as such, not glossed over
