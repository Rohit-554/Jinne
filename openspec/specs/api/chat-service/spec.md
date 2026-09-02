# Chat Service Specification

## Purpose

Expose the existing conversation engine and memory store to a browser client over HTTP, without duplicating or changing their behavior - the API is a new consumer, the same relationship the CLI and evaluation harness already have.

## Requirements

### Requirement: Chat Turn Endpoint
The service SHALL expose an HTTP endpoint that accepts a user message and returns the companion's response for that turn, produced by the existing conversation engine.

#### Scenario: Chat endpoint returns a response
- **WHEN** a client sends a message to the chat endpoint
- **THEN** it receives the companion's text response for that turn

### Requirement: Streamed Response
The chat endpoint SHALL support streaming the assistant's response to the client incrementally as it is generated, rather than only after the full response is complete.

#### Scenario: Client receives incremental chunks
- **WHEN** a client makes a streaming chat request
- **THEN** it receives the response as a sequence of chunks that concatenate to the full response, not a single block delivered only at the end

### Requirement: Turn Memory Metadata
The chat endpoint SHALL report, for the turn just completed, which memories were retrieved as context, which new memories were created, and which existing memories were updated (superseded) as a result.

#### Scenario: Contradiction is reflected in turn metadata
- **WHEN** a user's message causes an existing memory to be superseded by a new one
- **THEN** the turn's response metadata includes both the newly created memory and the memory it superseded

#### Scenario: Turn with no memory changes reports empty lists
- **WHEN** a turn produces no new or updated memories
- **THEN** the turn's response metadata reports empty created and updated memory lists, not an error

### Requirement: Basic Active Memories List
The service SHALL expose an HTTP endpoint that lists all currently ACTIVE memories.

#### Scenario: Listing returns only active memories
- **WHEN** a client requests the memories list
- **THEN** the response includes only memories with status ACTIVE
