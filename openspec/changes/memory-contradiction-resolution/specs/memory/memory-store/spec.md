## ADDED Requirements

### Requirement: Memory Status Update
The system SHALL support updating an existing memory record's status and `valid_until` in place, without deleting the record or creating a new one.

#### Scenario: Superseded memory keeps its identity
- **WHEN** an existing memory's status is updated from ACTIVE to SUPERSEDED
- **THEN** the record retains its original id and other historical fields, and a subsequent lookup by id still returns it with the updated status
