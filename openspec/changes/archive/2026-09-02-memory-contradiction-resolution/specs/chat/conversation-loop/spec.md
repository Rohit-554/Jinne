## ADDED Requirements

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
