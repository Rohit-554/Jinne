# Companion AI Memory & Evaluation System

A temporal memory architecture for an AI companion: semantic retrieval separated from memory truth, contradictions and uncertainty handled explicitly, and long-range recall and persona consistency measured, not assumed.

This is not a chatbot demo. It's a small memory research prototype whose actual claim is: **structured, persistent memory with explicit contradiction resolution outperforms simpler approaches specifically where it matters (surviving a restart, resolving competing facts), and that gap is measured, not asserted.**

## The Problem

An AI companion that only has conversation-window context forgets everything the moment the window fills or the process restarts, and has no principled way to know that "I left Google and joined Microsoft" should replace "I work at Google" rather than sit alongside it as an equally-true fact. This project builds and evaluates a system that:

1. Remembers important facts across restarts.
2. Decides what's worth remembering (and what isn't).
3. Retrieves the right memories at the right time, semantically.
4. Updates or retires memories when the user's situation changes, without losing history.
5. Keeps a companion persona consistent over long conversations.
6. Is evaluated with repeatable, measured tests — including against simpler baselines.

Full requirements: [PLANNING.md](PLANNING.md). Repo conventions and stack: [CLAUDE.md](CLAUDE.md). Architecture detail: [ARCHITECTURE.md](ARCHITECTURE.md).

## How to Run

```bash
# 1. Create a virtualenv and install
py -3.13 -m venv .venv
.venv/Scripts/pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# edit .env: add a free Groq API key (console.groq.com) as GROQ_API_KEY

# 3. Chat
.venv/Scripts/python -m src.cli
```

In the CLI:
- Type anything to talk to the companion (default persona: **Mira**).
- `/memories` (or `/memory-timeline`) — see stored memories grouped by type, including superseded history.
- `/memory-debug` — see the score breakdown (similarity, importance, recency, confidence) for what was just retrieved.
- `/exit` to quit.

Run the test suite: `.venv/Scripts/python -m pytest`
Run the evaluation harness: `.venv/Scripts/python -m src.evaluation.run_eval`

## Memory Model

Each memory is a structured record, not just an embedded blob:

```text
Memory { id, type, subject, relation, value,
         status, importance, confidence,
         created_at, updated_at, valid_from, valid_until,
         supersedes_memory_id, source_message_id, embedding }
```

`status` is one of `ACTIVE`, `SUPERSEDED`, or `UNCERTAIN`. `type` is a small taxonomy (`IDENTITY`, `RELATIONSHIP`, `PREFERENCE`, `CAREER`, `GOAL`, `PLAN`, `EVENT`, `TEMPORARY_STATE`, `EXPERIENCE`, `PERSON`, `LOCATION`, `OTHER`) that also drives decay rate. See [PLANNING.md's Memory Model](PLANNING.md#5-memory-model) for the full rationale.

## Extraction Strategy

Every user message goes through an LLM call constrained by a taxonomy-aware prompt and a Pydantic schema, deciding SAVE or IGNORE per candidate fact (multiple facts can come from one message). "I'm eating pizza right now" is ignored; "Pizza has been my favourite food since childhood" is saved. Malformed LLM output fails validation loudly rather than silently corrupting the store — and when it does fail, the conversation continues anyway (see Known Limitations).

## Retrieval Strategy

Embeddings (via a local `fastembed` model, no API key required) find candidates; a hybrid score ranks them:

```text
final_score = 0.6 * semantic_similarity
            + 0.2 * importance
            + 0.1 * confidence
            + 0.1 * recency_factor(type, age)
```

`recency_factor` is exponential decay with a half-life set per memory type — a day or so for `TEMPORARY_STATE`, effectively non-decaying within a prototype's timeframe for `IDENTITY`/`RELATIONSHIP`. Decay only affects ranking; it never touches stored data. Only ACTIVE memories are retrieved for current context; a separate `retrieve_historical` call over SUPERSEDED memories powers "what did I have before this?" questions, kept explicitly labeled as past state in the prompt so the model never presents history as current.

## Contradiction Handling

The `MemoryResolver` is the piece that makes this more than a vector store with extra steps. For each new SAVE candidate:

1. Look up existing ACTIVE memories with the same subject+relation. None found → insert as a new independent fact, no LLM call needed.
2. Found some → one LLM call classifies the relationship: **DUPLICATE** (same fact restated, nothing created), **SUPERSEDE** (mutually exclusive with an existing fact — mark it SUPERSEDED, insert the new one ACTIVE, linked via `supersedes_memory_id`), or **INDEPENDENT** (can coexist, e.g. liking both Kotlin and Python — insert without touching the existing memory).
3. Low-confidence candidates (a fixed threshold on the extractor's own confidence score, not another LLM call) are stored as `UNCERTAIN` instead of `ACTIVE`, and never supersede anything.

Verified live: "I work at Google" → "I left Google and joined Microsoft" → "Where do I work?" answers Microsoft; "Where did I work before Microsoft?" answers Google; "I like Kotlin" + "I also like Python" leaves both ACTIVE.

## Temporal Memory & Persona Consistency

Temporal reasoning falls out of the resolver + historical retrieval combination above — current and historical truth are structurally distinct (`status`), not something the model has to infer from a raw transcript alone. Persona (a static, hand-authored character — see [PLANNING.md's Persona System](PLANNING.md#15-persona-system)) is stored entirely separately from user memory and rendered into every prompt's system message, so "who is the companion" never gets contaminated by "who is the user."

## Why Hybrid Memory Was Chosen (and What the Alternatives Actually Do)

Full writeup with real numbers: [eval/BASELINE_COMPARISON.md](eval/BASELINE_COMPARISON.md). Short version: on the 50-scenario suite, the proposed system scores 98%, and two simpler baselines — full raw context with no memory at all, and naive vector memory with no resolver — both score 96%. That gap looks small, and the honest reason is that every scenario runs in one short session that fits entirely in raw context, which isn't the condition persistent structured memory is actually necessary for. Two things are worth separating:

- **Where structured memory is not optional**: surviving a process restart. Neither baseline can do this at all — proven live in the P0 milestone (tell the companion a fact, close the process, open a new one with zero in-memory state, ask again, get the right answer from SQLite alone).
- **Where the resolver's value shows up even in-session**: the one scenario where baselines failed and the proposed system passed, the raw-context baseline gave a real non-answer — it hedged and asked the user which of two stated facts was current, instead of confidently resolving it. That's the exact failure mode the resolver exists to prevent.

**What was tried and abandoned along the way:**
- A unified `retrieve(status=[...])` method instead of separate `retrieve`/`retrieve_historical` — kept them separate; call sites read more clearly when "give me current facts" and "give me history" are different method names.
- Calling the resolver's LLM on every SAVE candidate — changed to skip the call entirely when no existing memory shares the candidate's subject+relation, since there's nothing ambiguous to resolve and no reason to spend a call on it.
- Detecting uncertain/hedged statements with a second LLM call — replaced with a deterministic threshold on the confidence the extractor already outputs, reproducible and free.

## Evaluation Methodology & Actual Results

50 scenarios (10 each: factual recall, long-range recall, contradiction/update, temporal reasoning, persona consistency), replayed end-to-end through the real `ConversationEngine` — not mocks. Factual categories are graded by deterministic substring match (after normalizing common Unicode punctuation variants); persona consistency is graded by an LLM judge (PASS/FAIL/PARTIAL + reasoning), whose known limitations (judge bias, nondeterminism, same-model-family correlation) are documented rather than hidden.

**Actual measured result: 98% overall (49/50).** Per-category: factual recall 100%, long-range recall 100%, contradiction/update 100%, temporal reasoning 100%, persona consistency 90%. Full detail, including the one genuine failure and how it was distinguished from a grading-artifact false positive: [eval/FAILURE_ANALYSIS.md](eval/FAILURE_ANALYSIS.md).

Getting a clean run took three attempts across four different Groq API keys — the free tier's daily token cap was hit repeatedly during evaluation. That's disclosed in the failure analysis rather than smoothed over: every reported number comes from a scenario that actually completed against a live model, never a rate-limit failure.

## Known Limitations

- **LLM extraction occasionally produces malformed JSON** (an extra bracket, a missing quote) — caught by schema validation and logged, at the cost of that one fact not being saved for that turn. Inherent to LLM-based structured output; not eliminated, only contained.
- **Deterministic grading can false-negative on a correct-but-differently-worded answer.** Found and partially fixed (Unicode hyphen variants normalized) during evaluation; a genuinely paraphrase-tolerant grader would need semantic (not substring) matching, which is a larger undertaking than this prototype's scope.
- **LLM-as-judge for persona consistency inherits the same-model-family bias risk** — the model judging responses is from the same provider as the model generating them.
- **The evaluation suite's scenarios are all single-session and short**, so they under-measure the case (cross-session persistence) where the architecture is most clearly necessary rather than merely helpful — see the baseline comparison writeup above.
- **Hybrid retrieval weights are fixed constants, not tuned** against real usage data.
- Three real bugs were found and fixed via live testing during development, not just unit tests: a Windows console crash on emoji output, a context-rendering bug that caused the model to confuse the user with their own dog, and unhandled exceptions that could crash the whole CLI mid-turn. All are covered by regression tests now.
- **The resolver only compares a new candidate against existing memories sharing the exact same `relation` string.** Found live during final demo verification: "I'm dating Sarah" (`relation=dating`) and "Sarah and I broke up" (extracted as `relation=ex_partner`) are semantically about the same real-world state, but because the extractor didn't reuse the same relation label, the resolver never even considered them related — both stayed ACTIVE side by side instead of the breakup superseding the relationship status. Same pattern with "I left Stripe" producing both a correctly-superseded `works_at` record and a separate, redundant `previous_employer` record. This did not cause an incorrect answer in that run (the direct current/historical questions were still answered correctly), but it does leave the raw memory store messier than it should be. A real fix (e.g. broadening the resolver's candidate lookup to "same type," not just "same relation") is an architecture change that needs its own design pass, not a rushed patch - left as a named next improvement rather than patched under time pressure.

## Next Improvements

- Broaden the resolver's candidate lookup from "exact relation match" to "same subject+type," so semantically-linked facts under different relation labels (e.g. `dating` vs `ex_partner`) can be reconciled instead of coexisting as stale duplicates (see Known Limitations).
- Entity-overlap as a fifth retrieval scoring signal (mentioned in PLANNING.md's Retrieval Strategy, not implemented here).
- Tune hybrid-score and decay weights against a larger, human-labeled scenario set.
- `/eval` as an in-CLI command instead of a separate script.
- A semantic (LLM- or embedding-based) grading fallback for deterministic categories, to reduce false negatives from paraphrasing.
- Expand persona-consistency scenarios and cross-check the LLM judge against a second, differently-sourced model to reduce same-family bias risk.

## Demo Script

A scripted walkthrough proving persistence, contradiction handling, and explainability in one sitting:

```text
$ python -m src.cli
Mira is here. Type /exit to quit, /memories for the timeline, /memory-debug for the last retrieval.
> I'm dating Sarah.
> I work at Stripe.
> I'm training for a marathon.
> /exit

$ python -m src.cli          # fully restarted process, zero in-memory state
> What do you remember about me?        # -> recalls Sarah, Stripe, marathon training
> Sarah and I broke up.
> I've been feeling lonely lately.      # -> response uses the breakup naturally
> I left Stripe and joined OpenAI.
> Where do I work?                      # -> OpenAI
> Where did I work before?              # -> Stripe
> What was I training for?              # -> a marathon
> /memories                             # -> shows CAREER: Stripe SUPERSEDED, OpenAI ACTIVE
> /memory-debug                         # -> shows the score breakdown behind the last answer
> /exit
```

This mirrors [PLANNING.md's Demo Story](PLANNING.md#28-demo-story) exactly. It was verified against the live CLI as part of this project's final testing pass (see the commit history for that verification).
