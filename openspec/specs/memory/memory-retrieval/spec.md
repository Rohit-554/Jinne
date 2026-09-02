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

### Requirement: Historical Memory Retrieval
The system SHALL support retrieving SUPERSEDED memories ranked by semantic similarity to a message, as an operation distinct from the existing ACTIVE-only retrieval.

#### Scenario: Historical retrieval finds a superseded fact
- **WHEN** a memory about the user's previous employer has been superseded by a newer one, and the user asks where they worked before their current employer
- **THEN** historical retrieval returns the superseded employer memory among its results

#### Scenario: Historical retrieval excludes ACTIVE memories
- **WHEN** historical retrieval is run
- **THEN** memories with status ACTIVE are not included in its results

### Requirement: Hybrid Ranking Signals
Retrieval SHALL rank candidate memories using a combination of semantic similarity, importance, confidence, and recency, not semantic similarity alone.

#### Scenario: Higher-importance memory ranks above a more similar but low-importance one
- **WHEN** two candidate memories have similar semantic similarity to the query, but one has substantially higher importance
- **THEN** the higher-importance memory ranks at or above the other in the returned order

### Requirement: Recency Decay by Memory Type
A memory's contribution to its retrieval score SHALL decrease as it ages, at a rate that depends on its memory type, without altering the memory's stored status or deleting it.

#### Scenario: Temporary state fact decays faster than an identity fact
- **WHEN** a TEMPORARY_STATE memory and an IDENTITY memory of the same age and similar similarity/importance are both candidates
- **THEN** the TEMPORARY_STATE memory's recency contribution to its score is lower

#### Scenario: Decay does not change stored data
- **WHEN** a memory's retrieval score is reduced by decay
- **THEN** the memory's status, importance, confidence, and other stored fields are unchanged

### Requirement: Scored Retrieval with Explainable Breakdown
The system SHALL support retrieving candidate memories along with their individual score components (semantic similarity, importance weight, recency weight, confidence weight, and final combined score).

#### Scenario: Score breakdown is available per candidate
- **WHEN** scored retrieval is run for a message
- **THEN** each returned candidate includes its semantic similarity, importance weight, recency weight, confidence weight, and final score
