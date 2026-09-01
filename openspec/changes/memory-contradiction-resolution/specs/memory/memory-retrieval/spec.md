## ADDED Requirements

### Requirement: Historical Memory Retrieval
The system SHALL support retrieving SUPERSEDED memories ranked by semantic similarity to a message, as an operation distinct from the existing ACTIVE-only retrieval.

#### Scenario: Historical retrieval finds a superseded fact
- **WHEN** a memory about the user's previous employer has been superseded by a newer one, and the user asks where they worked before their current employer
- **THEN** historical retrieval returns the superseded employer memory among its results

#### Scenario: Historical retrieval excludes ACTIVE memories
- **WHEN** historical retrieval is run
- **THEN** memories with status ACTIVE are not included in its results
