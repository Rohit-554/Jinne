## Purpose

Give a reviewer a dark, minimal chat interface that talks to the real companion backend and shows, at a glance, that the companion has persistent memory - without yet building the deeper inspector/timeline/persona/evaluation views FRONTENDPLAN.md scopes to later phases.

## ADDED Requirements

### Requirement: Dark-Themed Chat Page
The frontend SHALL present a dark-themed chat page showing the companion's name, a short persona description, the message history, and a message input.

#### Scenario: Chat page loads with companion identity visible
- **WHEN** the chat page loads
- **THEN** the companion's name and a short persona description are visible alongside the message history and input

### Requirement: Send a Message
The frontend SHALL let the user type a message and send it to the backend, appending it to the visible message history.

#### Scenario: Sent message appears in history
- **WHEN** the user types a message and sends it
- **THEN** that message appears in the message history

### Requirement: Streaming Assistant Response Rendering
The frontend SHALL render the assistant's response incrementally as chunks arrive from the backend, not only once the full response is complete.

#### Scenario: Response text grows as chunks arrive
- **WHEN** the backend streams a response for the user's message
- **THEN** the displayed assistant message grows incrementally rather than appearing all at once after the full response is received

### Requirement: Minimal Active Memories Panel
The frontend SHALL show a collapsible panel listing the companion's currently active memories, fetched from the backend.

#### Scenario: Active memories are listed
- **WHEN** the active memories panel is open and the companion has active memories
- **THEN** each active memory's value is visible in the panel

#### Scenario: Empty state when no memories exist yet
- **WHEN** the companion has no active memories
- **THEN** the panel shows a plain empty-state message instead of an empty list or an error
