## Purpose

Provide durable, structured storage for companion memory records that survives application restarts and acts as the source of truth for what is currently believed to be valid, as distinct from what is merely semantically similar.

## ADDED Requirements

### Requirement: Persisted Memory Storage
The system SHALL persist memory records to durable on-disk storage such that they remain available after the application process restarts.

#### Scenario: Memory recalled after restart
- **WHEN** a memory record is stored during one application run and the application is stopped and restarted
- **THEN** a subsequent query for that memory returns the previously stored record

### Requirement: Structured Memory Record
Each stored memory record SHALL include the fields: id, type, subject, relation, value, status, importance, confidence, created_at, updated_at, valid_from, valid_until, supersedes_memory_id, and source_message_id.

#### Scenario: New memory record has required fields
- **WHEN** a new memory is saved
- **THEN** the stored record includes a unique id, a type drawn from the memory taxonomy, subject/relation/value, a status, importance, confidence, and created_at/updated_at timestamps

### Requirement: Active Memory Query
The system SHALL support querying stored memories filtered by lifecycle status.

#### Scenario: Query returns only ACTIVE memories
- **WHEN** the store is queried for memories with status ACTIVE
- **THEN** records with any other status are excluded from the result
