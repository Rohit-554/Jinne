# Memory Resolver Specification

## Purpose

Decide how a newly extracted SAVE candidate relates to what the system already believes, so contradictory facts update current truth instead of accumulating as separate active memories, while independent facts and uncertain statements are handled distinctly.

## Requirements

### Requirement: Duplicate Detection
When a new SAVE candidate expresses the same fact as an existing ACTIVE memory with the same subject and relation, the resolver SHALL treat it as a duplicate and SHALL NOT create a new memory record.

#### Scenario: Identical fact restated
- **WHEN** the user restates a fact that exactly matches an existing ACTIVE memory's subject, relation, and value
- **THEN** no new memory record is created

### Requirement: Contradiction Superseding
When a new SAVE candidate's subject and relation match an existing ACTIVE memory but represent a mutually exclusive current value, the resolver SHALL mark the existing memory SUPERSEDED and insert the new candidate as an ACTIVE memory linked to it via `supersedes_memory_id`.

#### Scenario: Career change supersedes the old employer
- **WHEN** an ACTIVE memory states the user works at Google, and the user says "I left Google and joined Microsoft"
- **THEN** the Google memory's status becomes SUPERSEDED and a new ACTIVE memory is created for Microsoft with `supersedes_memory_id` pointing at the Google memory

### Requirement: Independent Fact Handling
When a new SAVE candidate does not duplicate or contradict any existing ACTIVE memory (including when it shares a subject and relation with an existing memory that can coexist with it, such as multiple simultaneous preferences), the resolver SHALL insert it as a new ACTIVE memory without altering existing memories.

#### Scenario: First mention of a fact
- **WHEN** no existing memory shares the candidate's subject and relation
- **THEN** the candidate is inserted as a new ACTIVE memory

#### Scenario: Coexisting preference is not treated as a contradiction
- **WHEN** an ACTIVE memory states the user likes Kotlin, and the user separately says they also like Python
- **THEN** both memories remain ACTIVE and neither supersedes the other

### Requirement: Uncertainty Handling
When a SAVE candidate's confidence falls below the configured certainty threshold, the resolver SHALL persist it with status UNCERTAIN instead of ACTIVE, and SHALL NOT supersede any existing memory on its behalf.

#### Scenario: Hedged statement is stored as uncertain
- **WHEN** the user says "I might move to Bangalore next year" and the extracted candidate's confidence is below the certainty threshold
- **THEN** the resulting memory is stored with status UNCERTAIN rather than ACTIVE, and no existing ACTIVE memory is superseded
