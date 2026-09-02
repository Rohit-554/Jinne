## ADDED Requirements

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
