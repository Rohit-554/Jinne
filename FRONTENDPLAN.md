# FRONTENDPLAN.md

## Project: Companion AI Frontend

## 1. Goal

Build a polished dark-themed frontend that makes the companion's invisible memory architecture easy to understand and impressive to demo.

The frontend is not the core assignment. It is a presentation layer on top of the working Python memory engine.

The UI should help a reviewer immediately see:

- the conversation
- what the companion remembers
- which memories are active or outdated
- why a memory was retrieved
- how the companion persona is defined
- how the evaluation system is performing

The frontend should make the project feel like a thoughtful AI systems prototype rather than a generic chatbot.

## 2. Recommended Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui or lightweight custom components
- Lucide icons
- Framer Motion only for subtle transitions
- Recharts for evaluation metrics if needed

### Backend Integration
- Python backend
- FastAPI
- REST for normal reads/writes
- WebSocket or Server-Sent Events for streaming chat responses

```text
React + TypeScript
        |
        v
      FastAPI
        |
        v
Conversation Engine
        |
        +-- Persona Manager
        +-- Memory Extractor
        +-- Memory Retriever
        +-- Memory Resolver
        +-- Evaluation Engine
        |
        v
SQLite + Embeddings
```

## 3. Frontend Principles

The frontend should be:

- dark
- minimal
- premium
- technical
- calm
- easy to scan
- highly observable
- demo-friendly

Avoid:

- gradients everywhere
- neon cyberpunk styling
- excessive animation
- glassmorphism overload
- generic SaaS dashboard feel
- fake metrics
- unnecessary settings

The product should feel closer to a developer tool / research prototype than a consumer social app.

## 4. Visual Direction

Suggested palette:

```text
Background       #0B0D10
Primary surface  #111419
Secondary        #171B21
Border           #252B33
Primary text     #F4F7FA
Secondary text   #9EA7B3
Accent           #8EDB5B
Warning          #E9B949
Error            #E56A6A
```

Do not overuse accent colors.

## 5. Typography

Recommended:

- Geist or Inter for headings/body
- Geist Mono or JetBrains Mono for metadata

## 6. Main Layout

Desktop:

```text
+---------------------------------------------------------------+
| Logo / Companion Name                      Eval | Memories     |
+----------------------+----------------------------------------+
|                      |                                        |
|        CHAT          |          MEMORY INSPECTOR              |
|                      |                                        |
|                      |                                        |
+----------------------+----------------------------------------+
|               Message Input                                  |
+---------------------------------------------------------------+
```

Recommended split:

```text
65% Chat
35% Memory Inspector
```

The right panel should be collapsible.

## 7. Conversation Area

Show:

- companion name
- short persona description
- current memory status
- message history
- streaming assistant responses
- user input
- send button

Optional small badge on AI responses:

```text
Used 2 memories
```

Clicking it should open the retrieval details for that response.

## 8. Companion Header

Example:

```text
Mira
Warm, curious, slightly sarcastic

● Memory system active
3 relevant memories in context
```

## 9. Memory Inspector

Tabs:

```text
Active
Timeline
Retrieved
Persona
```

### Active
Shows currently valid memories.

Example:

```text
CAREER

Works at Microsoft
Android Engineer

importance 0.92
confidence 0.97
ACTIVE
```

## 10. Memory Timeline

One of the strongest demo features.

```text
CAREER

Jan 2026
Google
SUPERSEDED
     |
     v
Aug 2026
Microsoft
ACTIVE
```

Relationship example:

```text
Dating Sarah
     |
     v
Breakup with Sarah
```

Clearly distinguish:

- ACTIVE
- SUPERSEDED
- EXPIRED
- UNCERTAIN

## 11. Retrieved Memories Panel

For each response, show why memories were selected.

```text
Retrieved for:
"I'm nervous about tomorrow."

1. Stripe interview tomorrow
   semantic relevance   0.89
   importance           0.91
   recency              0.97
   final score          0.93
```

Also provide a human-readable reason:

```text
Why selected:
- highly related to "tomorrow"
- recent
- high importance
- currently active
```

## 12. Persona Panel

Example:

```text
Mira

Traits
Warm
Curious
Playful
Slightly sarcastic

Communication
Casual
Emotionally aware
Concise

Stable preferences
Likes science fiction
Dislikes horror
Values honesty
```

Only show persona scores if they come from real evaluation data.

## 13. Evaluation Dashboard

Route:

```text
/evaluation
```

Possible metrics:

```text
Memory Recall
Contradiction Resolution
Long-Range Recall
Persona Consistency
Temporal Reasoning
```

Never fabricate numbers.

Show individual test cases too:

```text
PASS

Long-range recall #08

Turn 2
"My dog is Bruno."

Turn 43
"What is my dog's name?"

Expected
Bruno

Actual
Bruno
```

Failures should also be visible.

## 14. Baseline Comparison

If implemented:

```text
                     Recall    Contradictions
Conversation Only      ...          ...
Vector Only            ...          ...
Hybrid Memory          ...          ...
```

Prefer a compact table before spending time on charts.

## 15. Navigation

Keep it simple:

```text
Chat
Memories
Evaluation
Architecture
```

Suggested routes:

```text
/
/memories
/evaluation
/architecture
```

Architecture page is optional.

## 16. Memories Page

Provide:

- search
- status filters
- category filters
- memory cards
- timeline view

Possible status filters:

```text
ACTIVE
SUPERSEDED
EXPIRED
UNCERTAIN
```

## 17. Architecture Page

Optional static diagram:

```text
User
 |
 v
Conversation Engine
 |
 +--> Memory Retrieval
 |
 +--> Persona
 |
 v
LLM
 |
 v
Response
 |
 v
Memory Extraction
 |
 v
Contradiction Resolver
 |
 v
SQLite + Embeddings
```

## 18. Streaming UX

Recommended flow:

1. User sends message.
2. Assistant response streams.
3. Retrieved memory metadata becomes visible.
4. Newly created memories appear.
5. Updated memories change state.
6. Timeline refreshes.

Use subtle transitions only.

## 19. FastAPI Contract

### Chat

```text
POST /api/chat
```

Request:

```json
{
  "message": "I'm nervous about tomorrow."
}
```

Response:

```json
{
  "response": "The Stripe interview is tomorrow...",
  "retrieved_memories": [],
  "created_memories": [],
  "updated_memories": []
}
```

For streaming, use SSE or WebSocket.

### Memory

```text
GET /api/memories
GET /api/memories/{id}
GET /api/memories/timeline
GET /api/memories/retrieval/{message_id}
```

### Persona

```text
GET /api/persona
```

### Evaluation

```text
GET /api/evaluation/latest
GET /api/evaluation/results
GET /api/evaluation/results/{scenario_id}
```

Optional:

```text
POST /api/evaluation/run
```

## 20. Suggested Frontend Structure

```text
frontend/
|
|-- src/
|   |-- components/
|   |   |-- chat/
|   |   |-- memory/
|   |   |-- persona/
|   |   |-- evaluation/
|   |   `-- ui/
|   |
|   |-- pages/
|   |   |-- ChatPage.tsx
|   |   |-- MemoriesPage.tsx
|   |   |-- EvaluationPage.tsx
|   |   `-- ArchitecturePage.tsx
|   |
|   |-- hooks/
|   |-- lib/
|   |-- api/
|   |-- types/
|   |-- store/
|   `-- App.tsx
|
|-- package.json
|-- vite.config.ts
`-- tsconfig.json
```

## 21. Core Components

### Chat
- ChatHeader
- ChatMessage
- MessageInput
- StreamingMessage
- MemoryUsageBadge

### Memory
- MemoryInspector
- MemoryCard
- MemoryStatusBadge
- MemoryTimeline
- RetrievedMemoryCard
- RetrievalScore

### Persona
- PersonaCard
- TraitList
- PersonaStatus

### Evaluation
- EvaluationSummary
- MetricCard
- ScenarioResult
- FailureCard
- BaselineComparison

## 22. State Management

Recommended:

- TanStack Query for backend/server state
- local React state for UI state

Avoid Redux unless a concrete need appears.

The backend should remain the source of truth.

## 23. Responsive Strategy

Desktop is the priority.

Desktop:

```text
Chat + Memory Inspector side-by-side
```

Tablet/mobile:

```text
Chat
Memory inspector becomes drawer or bottom sheet
```

Do not overspend time on mobile polish.

## 24. Motion

Use only subtle transitions:

- new memory appears
- state changes
- panel opens
- response streams
- timeline updates

Avoid distracting animation.

## 25. Error / Empty States

Examples:

```text
No long-term memories yet.

Important facts from your conversations
will appear here.
```

```text
No stored memories were needed for this response.
```

```text
Couldn't reach the companion engine.
Retry
```

Do not expose raw backend stack traces.

## 26. Demo Mode

Optional:

```text
Load Demo Scenario
```

This may seed deterministic starting data such as:

```text
User works at Stripe
User dates Sarah
User trains for a marathon
```

Do not fake evaluation results.

## 27. Key Demo Interaction

Existing:

```text
Dating Sarah
ACTIVE
```

User says:

```text
Sarah and I broke up.
```

UI changes to:

```text
Dating Sarah
SUPERSEDED

Breakup with Sarah
ACTIVE
```

Then user says:

```text
I've been feeling lonely.
```

Retrieved memory:

```text
Breakup with Sarah
```

The response uses that memory naturally.

This visually demonstrates extraction, contradiction handling, retrieval and response generation in one sequence.

## 28. Career Demo

Existing:

```text
Works at Stripe
ACTIVE
```

User:

```text
I joined OpenAI.
```

UI:

```text
Stripe
SUPERSEDED

OpenAI
ACTIVE
```

Then:

```text
Where did I work before?
```

The system retrieves Stripe as historical memory.

## 29. Implementation Priority

### P0
- Vite setup
- dark theme
- main chat
- FastAPI connection
- streaming
- basic memory inspector

### P1
- active memory cards
- retrieval inspector
- timeline
- persona panel

### P2
- evaluation dashboard
- scenario details
- failure display
- baseline comparison

### P3
- architecture page
- demo seeding
- subtle animations
- responsive polish

Do not start frontend polish before the backend core works reliably.

## 30. Build Order

```text
Step 1  Create Vite + React + TypeScript app
Step 2  Set up Tailwind and dark theme
Step 3  Build static ChatPage
Step 4  Build MemoryInspector
Step 5  Connect memory API
Step 6  Connect chat API
Step 7  Add response streaming
Step 8  Show retrieved memory metadata
Step 9  Implement active memories
Step 10 Implement memory timeline
Step 11 Add persona panel
Step 12 Create evaluation page
Step 13 Display real test results
Step 14 Add failure and baseline views
Step 15 Final visual polish
```

## 31. Scope Guardrail

Every visible frontend feature should help answer one of these questions:

```text
What does the companion remember?
Why did it remember that?
Is the memory still valid?
What did it remember before?
Why was this memory retrieved?
Is the companion staying consistent?
How well does the system perform?
```

If a feature does not support one of those questions, it is probably not worth building for this assignment.

## 32. Final Experience

The ideal first impression:

> This looks like a polished companion.

Then, within 30 seconds:

> This is actually a memory architecture debugger and evaluation system presented through a clean companion interface.

The UI exists to make the engineering work visible, not to distract from it.
