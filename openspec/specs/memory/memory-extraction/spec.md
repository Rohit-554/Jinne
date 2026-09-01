# Memory Extraction Specification

## Purpose

Decide, from each user message, which facts are worth remembering long-term versus which are conversational noise, so the memory store does not accumulate everything the user says.

## Requirements

### Requirement: Extraction Decision per Message
For each user message, the system SHALL produce zero or more memory candidates, each with a decision of SAVE or IGNORE.

#### Scenario: Stable personal fact is saved
- **WHEN** the user states a stable personal fact, such as "My dog's name is Bruno"
- **THEN** the extractor produces a SAVE decision with a memory candidate capturing that fact

#### Scenario: Conversational noise is ignored
- **WHEN** the user sends a greeting or trivial immediate-state message, such as "hi" or "I'm eating pizza right now"
- **THEN** the extractor produces no SAVE decisions for that message

### Requirement: Memory Type Classification
Each SAVE decision SHALL classify the memory candidate using the memory type taxonomy: IDENTITY, RELATIONSHIP, PREFERENCE, CAREER, GOAL, PLAN, EVENT, TEMPORARY_STATE, EXPERIENCE, PERSON, LOCATION, or OTHER.

#### Scenario: Career fact classified correctly
- **WHEN** the user says "I work at Google"
- **THEN** the resulting memory candidate has type CAREER, relation works_at, and value Google

### Requirement: Multiple Candidates per Message
The system SHALL support extracting more than one memory candidate from a single message when it contains multiple memory-worthy facts.

#### Scenario: Message with two facts yields two candidates
- **WHEN** the user says "I finally joined Microsoft as an Android engineer"
- **THEN** the extractor produces two SAVE candidates: one with relation works_at and value Microsoft, and one with relation job_role and value Android Engineer
