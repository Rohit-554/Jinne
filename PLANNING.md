# PLANNING.md

## Project: Companion AI Memory & Evaluation System

For repo conventions, tech stack, and standing engineering rules, see **CLAUDE.md**. This file is the project plan: the problem, the architecture, the memory model, the evaluation design, and the demo script.

## 1. Goal

Build a small but strong AI companion prototype whose main strength is **long-term memory and personality consistency**.

This is not a full chatbot product. The assignment is focused on the companion's core reasoning and memory loop.

The system should prove that it can:

1. Remember important facts across application restarts.
2. Decide what information is worth remembering.
3. Retrieve the right memories at the right time.
4. Update or retire memories when the user's situation changes.
5. Preserve historical facts without confusing them with current facts.
6. Maintain a stable companion personality over long conversations.
7. Evaluate these behaviors with repeatable tests and measurable results.

The project should feel like a **small memory research prototype**, not "ChatGPT with a database".

Primary focus: memory architecture, retrieval, update / contradiction handling, persona consistency.

Optional but highly valuable: evaluation harness, quantitative results, baseline comparison, failure analysis.

(See CLAUDE.md - Out of Scope for what not to build, and CLAUDE.md - Tech Stack for the recommended stack.)

## 2. Product Mental Model

The companion should behave like a person who keeps a useful notebook.

It should not remember everything.

It should remember important things, retrieve them when relevant, and understand that some things change over time.

Example:

User says:

> I work at Google.

Store:

```text
works_at = Google
status = ACTIVE
```

Later:

> I left Google and joined Microsoft.

Update:

```text
Google
status = SUPERSEDED

Microsoft
status = ACTIVE
```

Later:

> Where did I work before Microsoft?

The system should still be able to answer:

> Google.

Historical truth should be preserved without being treated as current truth.

## 3. Core Architecture

```text
User Message
    |
    v
Conversation Engine
    |
    +----------------------+
    |                      |
    v                      v
Memory Retriever      Persona Manager
    |                      |
    +----------+-----------+
               |
               v
          Context Builder
               |
               v
              LLM
               |
               v
        Companion Response
               |
               v
        Memory Extractor
               |
               v
        Memory Resolver
               |
               v
          Memory Store
```

Core components:

- Conversation Engine
- Persona Manager
- Memory Extractor
- Memory Resolver
- Memory Store
- Memory Retriever
- Context Builder
- Evaluation Harness

## 4. Storage Strategy

Use a **hybrid memory system**.

### Structured storage

Use SQLite as the source of truth.

SQLite stores:

- what the memory means
- whether it is currently valid
- when it became valid
- whether another memory replaced it
- importance
- confidence
- timestamps
- category
- entities
- lifecycle state

### Vector search

Use embeddings only for semantic retrieval.

Vectors answer:

> Which memories might be relevant to the current message?

Structured state answers:

> Which of those memories are currently valid?

Important design principle:

> Embeddings determine semantic relevance. Structured memory determines truth.

Do not make the vector database the source of truth.

For this prototype, avoid unnecessary hosted infrastructure such as Pinecone unless there is a strong reason.

Local options are preferred:

- SQLite + sqlite-vec
- SQLite + embeddings stored as arrays
- FAISS
- another lightweight local vector index

The dataset will be small enough that even simple cosine similarity may be acceptable.

## 5. Memory Model

Suggested memory representation:

```text
Memory
{
    id
    type
    subject
    relation
    value

    status
    importance
    confidence

    created_at
    updated_at
    valid_from
    valid_until

    supersedes_memory_id

    source_message_id

    embedding
}
```

Example:

```text
id: 42
type: CAREER
subject: user
relation: works_at
value: Microsoft

status: ACTIVE
importance: 0.92
confidence: 0.97

valid_from: 2026-08-01
supersedes_memory_id: 17
```

## 6. Memory Types

Start with a small explicit taxonomy.

Recommended categories:

```text
IDENTITY
RELATIONSHIP
PREFERENCE
CAREER
GOAL
PLAN
EVENT
TEMPORARY_STATE
EXPERIENCE
PERSON
LOCATION
OTHER
```

Do not over-engineer the taxonomy initially.

The goal is to make contradiction and retrieval behavior easier to reason about.

## 7. Memory Lifecycle

A memory should not simply be present or absent.

Suggested states:

```text
ACTIVE
SUPERSEDED
EXPIRED
UNCERTAIN
```

Possible future state:

```text
RETRACTED
```

### ACTIVE

Currently believed to be true.

### SUPERSEDED

Was previously true, but a newer memory replaced it.

Example:

```text
works_at = Google
SUPERSEDED

works_at = Microsoft
ACTIVE
```

### EXPIRED

A temporary fact whose useful lifetime has ended.

Example:

```text
Interview at Stripe on Friday
```

After Friday, it should no longer dominate current retrieval.

### UNCERTAIN

The user expressed uncertainty.

Example:

> I might move to Bangalore next year.

This should not become:

```text
User is moving to Bangalore
```

Instead:

```text
possible_plan = move to Bangalore
confidence = 0.55
status = UNCERTAIN
```

## 8. Memory Extraction

Every user message should be checked for memory-worthy information.

The extractor should output one of:

```text
SAVE
UPDATE
IGNORE
```

Potentially multiple memories can be extracted from one message.

Example:

> I finally joined Microsoft as an Android engineer.

Possible extraction:

```text
type: CAREER
relation: works_at
value: Microsoft

type: CAREER
relation: job_role
value: Android Engineer
```

### What should usually be remembered?

- stable personal facts
- relationships
- preferences
- career information
- meaningful goals
- future plans
- major events
- recurring concerns
- important people
- meaningful past experiences

### What should usually not be remembered?

- greetings
- filler
- one-off conversational noise
- trivial immediate-state information
- facts with no likely future usefulness

Example:

> I'm eating pizza right now.

Probably IGNORE.

But:

> Pizza has been my favourite food since childhood.

SAVE.

Good memory systems must know **what not to remember**.

## 9. Contradiction Handling

Contradiction handling is a major part of the assignment.

Example:

Existing memory:

```text
user works_at Google
ACTIVE
```

New statement:

> I left Google and joined Microsoft.

The resolver should identify that `works_at` is a single-current-value relationship.

Then:

```text
Google -> SUPERSEDED
Microsoft -> ACTIVE
```

Do not blindly append contradictory memories.

Do not delete historical facts unnecessarily.

The resolver should decide whether the new memory:

- duplicates an existing fact
- updates an existing fact
- contradicts an existing fact
- adds a new independent fact
- expresses uncertainty
- refers to past history instead of current truth

## 10. Temporal Memory

Time should be treated as first-class information.

Important distinction:

```text
CURRENT TRUTH
vs
HISTORICAL TRUTH
```

Example timeline:

```text
Jan 2026
Google
   |
   v
SUPERSEDED

Aug 2026
Microsoft
   |
   v
ACTIVE
```

This enables questions such as:

- Where do I work?
- Where did I work before?
- When did I change jobs?
- What was true last month?

A strong system should preserve history while prioritizing current truth.

## 11. Memory Decay

Not all memories deserve equal permanence.

Examples:

### Stable memory

```text
My sister's name is Ananya.
```

High durability.

### Temporary memory

```text
I am tired today.
```

Very short relevance window.

### Time-bound memory

```text
I have an interview on Friday.
```

High importance now, but should decay after Friday.

Possible decay factors:

- age
- memory type
- explicit expiration
- importance
- frequency of reinforcement
- whether it was superseded

Decay does not necessarily mean deletion.

It can simply reduce retrieval priority.

## 12. Retrieval Strategy

Do not use embedding similarity alone.

Recommended hybrid ranking:

```text
semantic similarity
+
importance
+
recency
+
entity overlap
+
confidence
+
memory status
+
temporal relevance
```

Conceptually:

```text
retrieval_score =
    semantic_similarity
  + importance_weight
  + recency_weight
  + entity_overlap_weight
  + confidence_weight
  + status_weight
```

Exact weights can be tuned later.

First retrieve candidate memories semantically.

Then rerank/filter using structured metadata.

Only the top few memories should reach the final LLM context.

Do not dump the entire memory database into the prompt.

## 13. Retrieval Example

Stored:

```text
User has Stripe interview tomorrow.
User's dog is Bruno.
User likes Kotlin.
User prefers tea.
```

Current message:

> I'm really nervous about tomorrow.

Expected retrieval:

```text
User has Stripe interview tomorrow.
```

The system should infer relevance beyond exact keyword matching.

## 14. Context Builder

The final model should receive a compact context containing:

1. Companion persona
2. Relevant active memories
3. Relevant historical memories if needed
4. Recent conversational context
5. User's current message

Example:

```text
PERSONA
Mira is warm, playful, curious, slightly sarcastic and avoids generic assistant language.

RELEVANT USER MEMORY
- User has a Stripe interview tomorrow.
- User has previously expressed anxiety about technical interviews.

RECENT CONTEXT
...

USER
I'm really nervous about tomorrow.
```

Only relevant memories should be injected.

## 15. Persona System

Create a clearly defined companion character.

Example:

```text
Name: Mira

Traits:
- warm
- curious
- playful
- slightly sarcastic

Communication:
- casual
- concise
- emotionally aware
- avoids corporate language
- avoids generic "AI assistant" phrasing

Stable preferences:
- likes science fiction
- dislikes horror movies
- values honesty
```

Persona should be stored separately from user memory.

User memory answers:

> Who is the user?

Persona state answers:

> Who is the companion?

The companion should remain consistent across 50+ turns.

## 16. Persona Drift Detection

Examples of failures:

Persona:

```text
Mira dislikes horror movies.
```

Later response:

```text
Horror movies are my favourite.
```

Failure.

Persona:

```text
Mira speaks casually.
```

Later:

```text
As an AI language model, I recommend...
```

Possible tone/personality drift.

Evaluation should explicitly test these cases.

## 17. Explainability / Memory Debugger

Add a CLI command such as:

```text
/memory-debug
```

It should show which memories were retrieved and why.

Example:

```text
Retrieved memories

1. Stripe interview tomorrow
   semantic_similarity: 0.89
   importance: 0.91
   recency: 0.97
   final_score: 0.93

2. Previous interview anxiety
   semantic_similarity: 0.78
   importance: 0.75
   final_score: 0.79
```

This makes the system easier to debug and demonstrate.

## 18. Memory Timeline

Add a CLI command:

```text
/memories
```

or:

```text
/memory-timeline
```

Example:

```text
CAREER

Jan 2026
Google
  status: SUPERSEDED

Aug 2026
Microsoft
  status: ACTIVE
```

This is an important differentiator.

## 19. Evaluation Harness

Build this after the core loop works.

Recommended categories:

```text
10 factual recall tests
10 long-range recall tests
10 contradiction/update tests
10 temporal reasoning tests
10 persona consistency tests
```

Target approximately 50 scenarios initially.

## 20. Example Evaluation Cases

### Basic recall

Turn 1:

> My dog is Bruno.

Turn 40:

> What's my dog's name?

Expected:

```text
Bruno
```

### Contradiction

Earlier:

> I work at Google.

Later:

> I left Google and joined Microsoft.

Question:

> Where do I work?

Expected:

```text
Microsoft
```

### Historical reasoning

Question:

> Where did I work before Microsoft?

Expected:

```text
Google
```

### Long-range recall

Turn 3:

> I'm training for a marathon.

Turn 55:

> What sport-related goal did I tell you about?

Expected:

```text
Marathon training
```

### Persona consistency

Persona:

```text
Mira dislikes horror movies.
```

Turn 60:

> Do you like horror movies?

Expected:

A response consistent with disliking horror.

## 21. Evaluation Metrics

Possible metrics:

```text
Memory extraction precision
Memory extraction recall
Relevant memory retrieval
Long-range recall
Contradiction resolution
Temporal reasoning
Persona consistency
```

Never fabricate metrics.

Only report actual measured results.

## 22. Baseline Comparison

If time allows, compare the system against simpler approaches.

Suggested baselines:

### Baseline A

Conversation context only.

No persistent memory.

### Baseline B

Naive vector memory.

All extracted messages embedded and retrieved only by vector similarity.

### Proposed system

Structured memory + temporal lifecycle + semantic retrieval + reranking.

This demonstrates whether architectural choices actually improve measurable behavior.

## 23. LLM-as-Judge

LLM-as-judge can be used for subjective properties such as persona consistency.

Possible output:

```text
PASS
FAIL
PARTIAL
```

Limitations must be documented:

- judge model bias
- nondeterminism
- evaluator and generation model correlation
- subjective interpretation
- false positives / false negatives

Where possible, use deterministic checks for factual memory tests.

## 24. Failure Analysis

Do not pretend the system is perfect.

Expected difficult areas:

- sarcasm
- ambiguous corrections
- uncertainty
- implied relationship changes
- multiple people with the same name
- conflicting dates
- user changing their mind repeatedly
- incorrect LLM extraction
- implicit references
- old facts that remain semantically similar to current facts

Documenting failures demonstrates engineering maturity.

## 25. Demo Story

The demo should tell one coherent story.

### Session 1

User:

> I'm dating Sarah.

> I work at Stripe.

> I'm training for a marathon.

Close the program.

### Session 2

Restart.

Ask:

> What do you remember about me?

Demonstrate persistence.

Then:

> Sarah and I broke up.

Demonstrate contradiction/update handling.

Then:

> I've been feeling lonely lately.

The response should use the breakup naturally.

Then:

> I left Stripe and joined OpenAI.

Demonstrate career update.

Ask:

> Where do I work?

Expected:

```text
OpenAI
```

Ask:

> Where did I work before?

Expected:

```text
Stripe
```

Later after many turns:

> What was I training for?

Expected:

```text
A marathon.
```

Finally run:

```text
/memory-timeline
```

and show lifecycle state.

## 26. Implementation Priorities

### P0: Core loop

Must work first.

- CLI conversation
- LLM integration
- SQLite persistence
- memory extraction
- memory storage
- semantic retrieval
- context injection

### P1: Memory intelligence

- contradiction detection
- superseding
- temporal state
- persona consistency
- importance
- confidence

### P2: Evaluation

- synthetic test scenarios
- automated runner
- factual pass/fail checks
- persona judge
- metrics
- failure logging

### P3: Differentiators

- hybrid reranking
- memory timeline
- memory debugger
- decay
- baseline comparison
- polished README
- architecture diagrams
- strong demo script

Do not work on P3 while P0 is unreliable.

## 27. Important Architectural Statement

The project should be able to defend this design decision clearly:

> Embeddings are used to discover semantically relevant memories, but they are not the source of truth. Structured memory tracks validity, confidence, temporal state and contradictions. Retrieval combines semantic similarity with structured signals before memories enter the LLM context.

## 28. README Must Explain

The final README should cover:

- what the problem is
- how to run the project
- architecture
- memory model
- extraction strategy
- retrieval strategy
- contradiction handling
- temporal memory
- persona consistency
- why hybrid memory was chosen
- what alternatives were considered
- what was tried and abandoned
- evaluation methodology
- actual results
- known limitations
- next improvements

Keep reasoning concrete.

## 29. Success Criteria

The project is successful when the following demo works reliably:

1. Tell the companion an important fact.
2. Restart the application.
3. Ask about it.
4. Companion remembers.
5. Change that fact.
6. Companion updates current truth.
7. Ask about the old truth.
8. Companion still understands the historical state.
9. Mention something indirectly related.
10. Relevant memory is retrieved naturally.
11. Run 50+ turns.
12. Persona remains consistent.
13. Run evaluation.
14. Produce measurable results.
15. Inspect memory timeline and retrieval reasoning.

## 30. Final Positioning

Do not position the submission as:

> I built an AI chatbot with memory.

Position it as:

> I built and evaluated a temporal memory architecture for an AI companion, separating semantic retrieval from memory truth, handling contradictions and uncertainty explicitly, and measuring long-range recall and persona consistency.

## 31. Starting Plan

Begin implementation in this order:

```text
Step 1
Define memory schema and SQLite tables.

Step 2
Create minimal CLI + LLM conversation loop.

Step 3
Add memory extraction.

Step 4
Persist extracted memories.

Step 5
Generate embeddings and implement candidate retrieval.

Step 6
Inject top relevant memories into companion context.

Step 7
Implement UPDATE / SUPERSEDE logic.

Step 8
Add temporal fields, importance and confidence.

Step 9
Add persona definition and consistency rules.

Step 10
Build /memories and /memory-debug.

Step 11
Write evaluation scenarios.

Step 12
Run baselines and collect real metrics.

Step 13
Write failure analysis.

Step 14
Polish README, architecture explanation and demo.
```

The first implementation milestone is:

> A user says "My dog's name is Bruno", closes the application, opens it again, asks "What is my dog's name?", and receives "Bruno" using the persistent memory system rather than previous chat context.
