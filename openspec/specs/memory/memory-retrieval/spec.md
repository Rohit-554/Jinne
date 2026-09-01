# Memory Retrieval Specification

## Purpose

Given the current conversation message, find which stored ACTIVE memories are semantically relevant, so that only a small, useful subset of memory ever reaches the LLM context.

## Requirements

### Requirement: Semantic Candidate Retrieval
The system SHALL retrieve stored ACTIVE memories ranked by semantic similarity to the current user message, using vector embeddings, without requiring exact keyword matches.

#### Scenario: Related memory retrieved without exact keyword overlap
- **WHEN** the user says "I'm really nervous about tomorrow" and a stored memory states that the user has a Stripe interview tomorrow
- **THEN** that memory is included among the top retrieved candidates

### Requirement: Bounded Result Set
The system SHALL return only a small, bounded number of top-ranked memories rather than the entire memory database.

#### Scenario: Retrieval result is capped
- **WHEN** retrieval is run against a memory store containing many stored memories
- **THEN** the number of memories returned does not exceed the configured top-k limit

### Requirement: Retrieval Excludes Inactive Memories
Retrieval SHALL only consider memories with status ACTIVE as candidates.

#### Scenario: Non-active memory not retrieved
- **WHEN** a memory's status is not ACTIVE
- **THEN** it is not returned by the retriever regardless of its semantic similarity to the current message
