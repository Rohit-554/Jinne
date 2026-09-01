# CLAUDE.md

## Project

Companion AI Memory & Evaluation System — a small memory research prototype whose core strength is long-term memory and personality consistency. Not a full chatbot product.

For the full problem statement, architecture, memory model, evaluation design, and demo script, see **PLANNING.md**. This file only covers how to work in this repo: stack, structure, and standing engineering rules. Active work is tracked as OpenSpec changes under `openspec/` (`openspec status`, `openspec/changes/`).

## Out of Scope

Do not spend time on any of the following unless it turns out to be required to make the core memory system work:

- Production UI, React/Android/mobile frontends, animations, avatars
- Authentication, login, user profiles, billing/payments
- Multi-user architecture
- Voice, image generation, video generation
- Production-scale infrastructure, cloud deployment, Kubernetes, microservices, Redis, Kafka
- Production observability stacks, load testing, large-scale deployment

A CLI or minimal script-based chat loop is enough. These constraints exist so the assignment's actual focus — memory architecture, retrieval, contradiction handling, and persona consistency — stays visible and doesn't get diluted by infrastructure work.

## Tech Stack

Use Python for the entire prototype.

```text
Language: Python 3.12+
CLI: Typer or simple argparse/input loop
LLM: OpenAI / Anthropic / Gemini API, configurable through environment variables
Structured storage: SQLite
ORM / DB access: SQLAlchemy or sqlite3
Embeddings: provider embedding API or a lightweight local embedding model
Vector retrieval: sqlite-vec, FAISS, or cosine similarity over stored embeddings
Validation / schemas: Pydantic
Testing: pytest
Evaluation data: JSON / JSONL
Environment config: python-dotenv
```

Preferred default implementation: Python + SQLite + Pydantic + SQLAlchemy + embeddings + lightweight local vector retrieval + pytest.

Keep the LLM provider behind a small interface so the model can be swapped without changing the memory architecture.

Do not introduce LangChain or another large agent framework unless it clearly reduces complexity. The important engineering work in this assignment is the memory extraction, lifecycle, retrieval, contradiction handling and evaluation logic, so those components should remain visible and understandable in our own code.

## Repo Structure

```text
companion-ai/
|
|-- src/
|   |-- chat/
|   |-- persona/
|   |-- memory/
|   |   |-- extractor/
|   |   |-- resolver/
|   |   |-- store/
|   |   |-- retriever/
|   |   |-- decay/
|   |   `-- models/
|   |
|   |-- llm/
|   |-- evaluation/
|   `-- cli/
|
|-- tests/
|   |-- recall/
|   |-- contradictions/
|   |-- temporal/
|   `-- persona/
|
|-- eval/
|   |-- scenarios/
|   |-- results/
|   `-- run_eval.*
|
|-- README.md
|-- ARCHITECTURE.md
|-- CLAUDE.md
|-- PLANNING.md
`-- .env.example
```

Adapt language-specific naming as needed.

## CLI Commands

```text
/chat
/memories
/memory-debug
/memory-timeline
/persona
/reset-session
/help
```

Optional: `/eval`.

Do not build a large CLI framework.

## Engineering Principles

- Keep the system understandable.
- Avoid infrastructure theatre.
- Optimize for correctness.
- Preserve historical truth.
- Treat uncertainty honestly.
- Do not remember everything.
- Make behavior observable.
- Measure behavior instead of relying on "it feels good".
- Never fabricate evaluation metrics. Only report actual measured results.

## Git Workflow

When implementing an OpenSpec change's `tasks.md`, commit and push incrementally instead of batching everything into one commit at the end:

1. Work through one task group at a time (a `## N. <heading>` section in `tasks.md`, e.g. "2. Memory Store").
2. After finishing all sub-tasks in that group, run that group's own verification steps (the tests/commands/behavior stated in each task's checkbox) and confirm they pass before moving on.
3. Once verified, `git add` only the files that group touched, commit with a message describing that group's change, and check off its tasks in `tasks.md` in the same commit.
4. `git push` immediately after each commit — don't let unpushed commits pile up.
5. If verification fails, fix the issue and re-verify before committing; never commit a task group that doesn't pass its own verification.

Commit messages: plain, descriptive, imperative mood (e.g. `Add SQLite memory store schema and CRUD`). **Do not add a `Co-Authored-By` trailer to commits in this repo.**

Remote: `origin` → `git@github.com-personal:Rohit-554/Jinne.git`, branch `master`.

## Where the Plan Lives

- **PLANNING.md** — goal, product mental model, architecture, memory model/types/lifecycle, extraction, contradiction handling, temporal memory, decay, retrieval strategy, context builder, persona system, evaluation harness, baselines, failure analysis, demo story, implementation priorities, success criteria, and the starting step-by-step plan.
- **openspec/** — the actual change proposals (spec deltas, design decisions, task checklists) implementing the plan incrementally. Run `openspec status` to see current changes.
