## Purpose

Tie persona, memory retrieval, extraction, and the LLM together into a CLI conversation loop, so that companion responses are grounded in relevant memory and persona, and facts persist across restarts.

## ADDED Requirements

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
