# Conversation Loop Specification

## Purpose

Tie persona, memory retrieval, extraction, and the LLM together into a CLI conversation loop, so that companion responses are grounded in relevant memory and persona, and facts persist across restarts.

## Requirements

### Requirement: CLI Conversation Loop
The system SHALL provide a command-line loop that accepts user text input, produces a companion text response, and continues until the user exits.

#### Scenario: Basic turn produces a response
- **WHEN** the user enters a message in the CLI
- **THEN** the companion prints a text response before prompting for the next input

### Requirement: Context Assembly
Before calling the LLM, the system SHALL assemble a context containing the companion persona, the relevant memories returned by retrieval, recent conversational turns, and the current user message.

#### Scenario: Relevant memory included in context
- **WHEN** retrieval returns one or more relevant memories for the current message
- **THEN** those memories are included in the context passed to the LLM for that turn

### Requirement: LLM Provider Abstraction
The system SHALL call the underlying LLM through a provider interface that can be reconfigured, such as via environment variables, without changing the memory or context-building logic.

#### Scenario: Provider swap does not affect memory logic
- **WHEN** the configured LLM provider is changed
- **THEN** memory extraction, storage, and retrieval behavior remain unchanged

### Requirement: End-to-End Persistence Across Restart
A fact told to the companion in one session SHALL be recallable in a later session after the application has been fully restarted.

#### Scenario: Dog's name recalled after restart
- **WHEN** the user tells the companion "My dog's name is Bruno", the application is closed, and the application is reopened
- **THEN** asking "What is my dog's name?" in the new session returns an answer containing "Bruno", sourced from persisted memory rather than in-process chat history

### Requirement: Resolved Memory Persistence
The system SHALL route each SAVE candidate through the memory resolver before persisting it, rather than inserting it directly, so that contradictory facts update current truth instead of accumulating as separate active memories.

#### Scenario: Contradictory statement updates current truth
- **WHEN** the user says "I left Google and joined Microsoft" and an ACTIVE memory already states they work at Google
- **THEN** after the turn completes, the Google memory is SUPERSEDED and a new ACTIVE memory states the user works at Microsoft

### Requirement: Historical Context Inclusion
When relevant SUPERSEDED memories are found for the current message, the system SHALL include them in the context passed to the LLM, labeled separately from current (ACTIVE) memory.

#### Scenario: Historical question surfaces past truth
- **WHEN** the user asks "Where did I work before Microsoft?" and a SUPERSEDED memory recording their previous employer is found
- **THEN** that memory is included in the LLM context in a section distinct from current memory, and the response reflects the historical fact rather than presenting it as current
