## Purpose

Provide simpler alternative conversation systems - no memory at all, and naive vector-only memory - so the proposed system's structured, hybrid memory architecture can be measured against something, not just asserted to be better.

## ADDED Requirements

### Requirement: Baseline A - Context-Only, No Persistent Memory
Baseline A SHALL respond to each turn using only the persona and the full raw conversation history sent so far in that scenario, with no extraction, retrieval, or persisted storage of any kind.

#### Scenario: Baseline A has no memory beyond the current conversation
- **WHEN** Baseline A completes a scenario
- **THEN** no memory record of any kind has been created or persisted for that scenario

### Requirement: Baseline B - Naive Vector Memory
Baseline B SHALL extract SAVE-worthy candidates the same way the proposed system does, embed and store every one of them, and retrieve relevant memories each turn purely by semantic similarity, without any lifecycle status, contradiction handling, or resolver step - so a superseded fact remains exactly as retrievable as the fact that replaced it.

#### Scenario: Baseline B retrieves both an old and a new fact for the same relation
- **WHEN** the user first states a fact and later contradicts it, and Baseline B is asked about the current state
- **THEN** both the original and the contradicting memory are equally eligible for retrieval by similarity, with nothing distinguishing which is current

### Requirement: Baselines Are Isolated Per Scenario
Each baseline SHALL run each scenario against its own fresh, isolated state, the same way the proposed system's evaluation does, so results are not contaminated across scenarios.

#### Scenario: Fresh baseline state per scenario
- **WHEN** two scenarios run in sequence against the same baseline
- **THEN** the second scenario's baseline state contains nothing carried over from the first
