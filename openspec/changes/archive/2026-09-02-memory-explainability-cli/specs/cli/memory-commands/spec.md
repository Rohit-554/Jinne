## Purpose

Make the memory system's internal state and retrieval reasoning visible from the CLI, so lifecycle transitions and retrieval scoring can be inspected and demonstrated instead of only asserted in tests.

## ADDED Requirements

### Requirement: Memory Timeline Command
The CLI SHALL support a `/memories` command that lists stored memories grouped by relation, showing each memory's value, status, and (when applicable) which memory it supersedes.

#### Scenario: Timeline shows a supersede chain
- **WHEN** the user runs `/memories` after a fact has been superseded by an update
- **THEN** the output shows both the superseded memory and the memory that replaced it, with their statuses, grouped under the same relation

### Requirement: Memory Debug Command
The CLI SHALL support a `/memory-debug` command that shows the retrieval score breakdown (semantic similarity, importance, recency, confidence, and final score) for the memories retrieved for the most recent conversation turn.

#### Scenario: Debug output shows score components
- **WHEN** the user runs `/memory-debug` after asking a question that triggered memory retrieval
- **THEN** the output lists each retrieved memory along with its semantic similarity, importance, recency, confidence, and final score

### Requirement: Commands Do Not Affect Conversation State
Running `/memories` or `/memory-debug` SHALL NOT create, modify, or delete any memory, and SHALL NOT count as a conversation turn.

#### Scenario: Debug command leaves memory untouched
- **WHEN** the user runs `/memory-debug` or `/memories`
- **THEN** no new memory record is created and no existing memory's fields change
