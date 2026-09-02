# Architecture

## Core Principle

> Embeddings are used to discover semantically relevant memories, but they are not the source of truth. Structured memory tracks validity, confidence, temporal state and contradictions. Retrieval combines semantic similarity with structured signals before memories enter the LLM context.

Every design decision in this system follows from that sentence. Vectors answer "what might be relevant." SQLite answers "what is currently true." The two are never conflated.

## Components

```text
User Message
    |
    v
Conversation Engine (src/chat/conversation_engine.py)
    |
    +----------------------+
    |                      |
    v                      v
Memory Retriever      Persona Manager
(src/memory/retriever) (src/persona)
    |                      |
    +----------+-----------+
               |
               v
          Context Builder
        (src/chat/context_builder.py)
               |
               v
              LLM
        (src/llm, Groq)
               |
               v
        Companion Response
               |
               v
        Memory Extractor
        (src/memory/extractor)
               |
               v
        Memory Resolver
        (src/memory/resolver)
               |
               v
          Memory Store
         (src/memory/store, SQLite)
```

- **Conversation Engine** — orchestrates a turn: retrieve, build context, call the LLM, then extract and store in the background. Never lets a memory-processing failure block the reply (see `chat/conversation_engine.py`'s exception handling around `extract_and_store`).
- **Persona Manager** (`src/persona`) — a static, hand-authored character (name, traits, communication style, stable preferences), rendered into every prompt's system message. Deliberately separate from user memory: "who is the companion" and "who is the user" are different questions.
- **Memory Extractor** (`src/memory/extractor`) — an LLM call, constrained by a taxonomy prompt and a Pydantic schema, that decides SAVE or IGNORE per candidate fact in a message. Validated output; malformed JSON fails loudly (caught and logged, never silently corrupting the store).
- **Memory Resolver** (`src/memory/resolver`) — the piece that makes contradiction handling real. For each SAVE candidate, it looks for existing ACTIVE memories sharing the same subject+relation. If none exist, the candidate is a new independent fact and no LLM call is needed. If some exist, an LLM call classifies the relationship as DUPLICATE, SUPERSEDE, or INDEPENDENT. Low-confidence candidates (a deterministic threshold, not another LLM call) are stored as UNCERTAIN instead of ACTIVE.
- **Memory Store** (`src/memory/store`, SQLite via SQLAlchemy) — the source of truth. Every memory has a lifecycle `status` (ACTIVE / SUPERSEDED / UNCERTAIN), timestamps, importance, confidence, and an optional `supersedes_memory_id` link. Status transitions mutate a row in place — a superseded memory keeps its id and history, it is never deleted.
- **Memory Retriever** (`src/memory/retriever`) — embeds the current message, embeds each stored memory once (at save time), and ranks ACTIVE candidates by a hybrid score: semantic similarity, importance, confidence, and a recency/decay factor that falls off at a rate set by the memory's type (fast for `TEMPORARY_STATE`, effectively negligible for `IDENTITY`/`RELATIONSHIP`). A separate `retrieve_historical` method runs the same scoring over SUPERSEDED memories, powering "what did I used to have before this?" questions.
- **Evaluation Harness** (`src/evaluation`, `eval/`) — replays a 50-scenario suite (10 each: factual recall, long-range recall, contradiction/update, temporal reasoning, persona consistency) through the real `ConversationEngine`, grading factual categories deterministically and persona consistency with an LLM judge. Also runs the same suite against two simpler baselines for comparison.

## Data Flow Through One Turn

1. User sends a message.
2. `MemoryRetriever.retrieve_scored` embeds the message, scores every ACTIVE memory (similarity + importance + confidence + recency), returns the top-k.
3. `MemoryRetriever.retrieve_historical` does the same over SUPERSEDED memories, so a question about the past can be answered without ever presenting old facts as current.
4. `ContextBuilder` assembles: persona block, `RELEVANT USER MEMORY` (current), `RELEVANT HISTORICAL MEMORY` (past, explicitly labeled as such), recent raw turns, and the current message.
5. The LLM produces a reply. It is returned to the user immediately.
6. In the background: `MemoryExtractor` decides SAVE/IGNORE per candidate fact in the message; each SAVE candidate is embedded and passed to `MemoryResolver`, which decides DUPLICATE (skip) / SUPERSEDE (mark the old memory SUPERSEDED, insert the new one ACTIVE, linked) / INDEPENDENT (insert as a new ACTIVE fact) / UNCERTAIN (low confidence, insert as UNCERTAIN). A failure anywhere in this step is caught and logged — it never breaks the conversation.

## Why Hybrid Memory, Not Just a Vector Store

A pure vector store (Baseline B in `eval/BASELINE_COMPARISON.md`) has no concept of "this fact replaced that one" — a superseded memory stays exactly as retrievable as its replacement forever. A pure raw-context approach (Baseline A) has no persistence at all — restart the process and everything is gone, and even within a session it can hedge and refuse to commit to which of two stated facts is current when nothing marks either fact more valid than the other. The structured status/resolver layer exists specifically to remove that ambiguity, and `eval/BASELINE_COMPARISON.md`'s `contra-08` example shows it happening in practice.
