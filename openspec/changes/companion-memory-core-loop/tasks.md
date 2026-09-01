## 1. Project Setup

- [x] 1.1 Create the repo structure from CLAUDE.md's Repo Structure section (`src/{chat,persona,memory/{extractor,resolver,store,retriever,models},llm,cli}`, `tests/`) and verify `python -c "import src"`-style imports resolve for each package (add `__init__.py` files as needed)
- [x] 1.2 Add `pyproject.toml`/`requirements.txt` with Python 3.12+, pydantic, sqlalchemy or sqlite3, python-dotenv, pytest, and an LLM SDK, and verify `pip install` (or equivalent) succeeds in a clean virtualenv
- [x] 1.3 Add `.env.example` documenting required environment variables (LLM provider, API key, model name, embedding model, SQLite path) and verify a copied `.env` is loaded by the app at startup

## 2. Memory Store (`memory/memory-store`)

- [x] 2.1 Define the `Memory` Pydantic model with fields id, type, subject, relation, value, status, importance, confidence, created_at, updated_at, valid_from, valid_until, supersedes_memory_id, source_message_id, embedding, and verify a unit test constructs a valid instance and rejects a missing required field
- [x] 2.2 Define the SQLite schema/table for memories (via SQLAlchemy models or raw DDL) and verify a migration/init script creates the table with all model fields
- [x] 2.3 Implement `MemoryStore.save(memory)` and `MemoryStore.get(id)` and verify a unit test saves a memory and reads back an identical record
- [x] 2.4 Implement `MemoryStore.list(status=...)` filtering by lifecycle status and verify a unit test confirms only ACTIVE records are returned when filtering by ACTIVE
- [x] 2.5 Verify persistence across restarts: a test writes to the SQLite file, closes the connection, reopens a fresh `MemoryStore` instance against the same file, and confirms the record is still present

## 3. LLM & Embedding Provider Interfaces

- [x] 3.1 Define `llm/provider.py` interfaces: `complete(messages) -> str` and `embed(text) -> list[float]`, and verify they are abstract/protocol types with no vendor-specific imports
- [x] 3.2 Implement one concrete provider (Groq for chat, fastembed for local embeddings) behind the interface, configured via environment variables, and verify a manual smoke call returns a non-empty completion and an embedding vector of the expected dimension
- [x] 3.3 Verify provider swap: a unit test injects a fake/stub provider implementing the same interface and confirms calling code built against the interface runs unchanged against it (extraction/retrieval modules built in later task groups depend only on this interface by construction, per design.md)

## 4. Memory Extraction (`memory/memory-extraction`)

- [x] 4.1 Define the extraction output schema (Pydantic) capturing decision (SAVE/IGNORE), type, subject, relation, value, importance, confidence per candidate, and verify invalid LLM output fails Pydantic validation in a unit test
- [x] 4.2 Write the extraction prompt encoding the memory taxonomy (PLANNING.md's Memory Types section) and SAVE/IGNORE guidance (PLANNING.md's Memory Extraction section), and implement `MemoryExtractor.extract(message) -> list[MemoryCandidate]` using the LLM provider
- [x] 4.3 Verify extraction behavior with recorded/mocked LLM responses: "My dog's name is Bruno" yields a SAVE candidate; "hi" and "I'm eating pizza right now" yield no SAVE candidates (also confirmed live against the real Groq model)
- [x] 4.4 Verify multi-fact extraction: "I finally joined Microsoft as an Android engineer" yields two SAVE candidates (works_at=Microsoft, job_role=Android Engineer) with a mocked LLM response (also confirmed live)
- [x] 4.5 Wire extraction to storage: after extraction, SAVE candidates are persisted via `MemoryStore.save` with status ACTIVE, and verify an integration test confirms a message results in a queryable stored memory

## 5. Memory Retrieval (`memory/memory-retrieval`)

- [x] 5.1 Implement embedding generation for stored memories (compute and store `embedding` on save) and verify a unit test confirms a saved memory has a non-null embedding
- [x] 5.2 Implement `MemoryRetriever.retrieve(message, top_k)` using cosine similarity over ACTIVE memory embeddings and verify a unit test returns memories ordered by descending similarity
- [x] 5.3 Verify the bounded result set: a store seeded with more than `top_k` memories returns exactly `top_k` results
- [x] 5.4 Verify status filtering: a store containing a non-ACTIVE memory confirms that memory is never returned regardless of similarity (seed one manually since this change does not yet produce non-ACTIVE memories)
- [x] 5.5 Verify semantic (non-keyword) retrieval: seed a memory "User has Stripe interview tomorrow" and query "I'm really nervous about tomorrow", and confirm it is retrieved (verified with real fastembed embeddings, matching PLANNING.md's Retrieval Example)

## 6. Persona

- [x] 6.1 Define a static persona configuration (name, traits, communication style, stable preferences) per PLANNING.md's Persona System section, stored in `persona/` separate from memory, and verify it loads without error at startup
- [x] 6.2 Implement a function that renders the persona into a context-ready text block and verify a unit test checks the rendered block contains name, traits, and communication style

## 7. Conversation Loop & Context Builder (`chat/conversation-loop`)

- [ ] 7.1 Implement the `ContextBuilder` that assembles persona block + retrieved memories + recent conversational turns + current user message into the LLM prompt, and verify a unit test confirms all four sections are present when memories are retrieved
- [ ] 7.2 Implement the `ConversationEngine` CLI loop (input → retrieve → build context → call LLM → print response → extract & store), and verify manually that a single turn produces a printed response
- [ ] 7.3 Wire the extraction step to run on every user message per turn (§4.5) inside the loop, and verify an integration test confirms a fact mentioned mid-conversation is present in the store afterward
- [ ] 7.4 Add a CLI entry point (`/chat` or default `python -m src.cli`) and a clean exit command, and verify the loop starts and exits without error

## 8. End-to-End Milestone Verification

- [ ] 8.1 Verify PLANNING.md's Starting Plan milestone end-to-end: run the CLI, say "My dog's name is Bruno", exit the process, restart the CLI, ask "What is my dog's name?", and confirm the response contains "Bruno"
- [ ] 8.2 Verify the response is sourced from persisted memory and not in-process history by confirming the answer is correct even when the process was fully restarted (no in-memory conversation state carried over)
- [ ] 8.3 Verify persona presence: ask an unrelated question and confirm the response tone/style matches the defined persona rather than generic assistant phrasing (manual/spot check)
