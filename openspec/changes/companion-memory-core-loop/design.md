## Context

Greenfield project (see PLANNING.md). No code exists yet. This change lays down the P0 "core loop" (PLANNING.md's Implementation Priorities and Starting Plan, steps 1–6) plus the minimal persona piece needed for context assembly: a CLI companion backed by SQLite, with LLM-driven extraction, embedding-based retrieval, and context injection. Contradiction/supersede resolution, temporal queries, decay, hybrid reranking, `/memory-debug`, `/memory-timeline`, persona drift detection, and the evaluation harness are explicitly deferred to follow-up changes (PLANNING.md P1–P3). See proposal.md - Why / What Changes for motivation and scope.

## Goals / Non-Goals

**Goals:**
- Establish the memory schema and repo structure the rest of the project builds on (PLANNING.md's Memory Model and CLAUDE.md's Repo Structure section), even though only a subset of fields is actively used by this change (e.g. `status` is always `ACTIVE`, `supersedes_memory_id` is always null).
- Make the LLM and embedding provider swappable behind small interfaces (CLAUDE.md's Tech Stack section) so later changes are not coupled to a specific vendor.
- Prove the milestone in PLANNING.md's Starting Plan (final milestone): "My dog's name is Bruno" → restart → "What is my dog's name?" → "Bruno", answered from persisted memory, not in-process chat history.

**Non-Goals:**
- Contradiction detection, UPDATE/SUPERSEDE logic, temporal/historical reasoning, decay, hybrid reranking beyond basic similarity + status filtering, memory debugger/timeline commands, persona drift detection, and the evaluation harness. These are separate follow-up changes.
- Multi-user support, auth, or any of the items in CLAUDE.md's Out of Scope section.

## Decisions

**SQLite as source of truth; embeddings for relevance only (PLANNING.md's Storage Strategy and Important Architectural Statement sections).** Structured fields in SQLite (`status`, timestamps, etc.) determine what is true; embeddings only narrow the candidate set semantically. Even though this change never sets `status` to anything but `ACTIVE`, the schema and the `WHERE status = 'ACTIVE'` filter are wired in now so later changes (contradiction handling) don't require a retrieval-layer rewrite. Alternative considered: treat a vector store as authoritative and skip the status filter — rejected because it would need to be unwound almost immediately.

**Embeddings stored as arrays in SQLite, cosine similarity computed in Python; no FAISS/sqlite-vec yet.** PLANNING.md's Storage Strategy section explicitly allows "even simple cosine similarity" for a small dataset. Adding FAISS or sqlite-vec now is unneeded complexity for a dataset that will realistically be dozens to low hundreds of rows in this milestone. Swapping in sqlite-vec/FAISS later only touches `memory/retriever`, not the store schema or the extraction/context-building logic. Alternative considered: sqlite-vec from day one — rejected as premature; revisit if retrieval latency or accuracy becomes a problem.

**LLM-based structured extraction with a fixed Pydantic output schema (SAVE/IGNORE + typed fields), not a hand-rolled rules engine.** PLANNING.md's Memory Extraction section needs judgment calls ("pizza right now" vs "favourite food since childhood") that are impractical to hand-code reliably. The extractor prompt constrains output to the taxonomy in PLANNING.md's Memory Types section and the SAVE/IGNORE/(UPDATE reserved) vocabulary in Memory Extraction, validated against a Pydantic model so malformed LLM output fails loudly instead of corrupting the store. Alternative considered: keyword/regex heuristics — rejected, cannot make the "is this memory-worthy" judgments PLANNING.md calls for.

**Provider interfaces for both the chat LLM and the embedding model, configured via environment variables (CLAUDE.md's Tech Stack section).** A single `llm/` module exposes a `complete(messages) -> text` interface and an `embed(text) -> vector` interface; concrete providers (OpenAI/Anthropic/Gemini) implement them. Memory extraction, retrieval, and the conversation loop depend only on these interfaces, never on a specific SDK. Alternative considered: call provider SDKs directly from each module — rejected, would make the provider swap CLAUDE.md's Tech Stack section asks for require touching every module.

**Repo layout follows CLAUDE.md's Repo Structure section exactly** (`src/{chat,persona,memory/{extractor,resolver,store,retriever,models},llm,cli}`, `tests/`), including an empty/placeholder `memory/resolver/` even though this change adds no resolver logic — so the follow-up contradiction-handling change has an obvious home and this change's directory structure doesn't need to be revisited.

**No LangChain or agent framework (CLAUDE.md's Tech Stack section).** Conversation loop, extraction, and retrieval are implemented directly so the memory logic stays visible, per CLAUDE.md's explicit instruction.

## Risks / Trade-offs

- [Naive cosine-similarity retrieval may scale poorly or feel imprecise as memory count grows] → Acceptable for the small dataset this milestone targets; isolated behind the retriever module so it can be swapped for sqlite-vec/FAISS without touching other capabilities.
- [LLM extraction can misclassify or hallucinate fields] → Pydantic validation rejects malformed output; extraction quality itself is left to be measured by the evaluation harness in a later change, not solved here.
- [Always-ACTIVE status means the store schema's lifecycle fields are exercised only partially by this change] → Intentional: proves persistence and retrieval first; contradiction handling (which exercises SUPERSEDED/UNCERTAIN) is scoped to its own change per PLANNING.md P1.
- [Local SQLite file path and provider API keys need environment configuration] → Use `python-dotenv` and a `.env.example`, per CLAUDE.md's Tech Stack section, so setup is a single documented step.

## Open Questions

None — remaining unknowns (retrieval scoring weights, contradiction rules, decay factors) are scoped to later changes and don't affect this change's specs or task breakdown.
