## Purpose

Give the companion a stable, explicitly defined character that every response draws on, kept separate from user memory so "who is the companion" is never confused with "who is the user".

## ADDED Requirements

### Requirement: Defined Companion Persona
The system SHALL define a companion persona including name, personality traits, communication style, and stable preferences, stored separately from user memory.

#### Scenario: Persona is available to context construction
- **WHEN** a response is generated
- **THEN** the persona's name, traits, communication style, and stable preferences are available for inclusion in the context

### Requirement: Persona Reflected in Responses
Companion responses SHALL be consistent with the defined persona's communication style, avoiding generic AI-assistant phrasing.

#### Scenario: Response avoids generic assistant language
- **WHEN** the companion responds to a user message
- **THEN** the response does not use disclaimers such as "As an AI language model" and instead reflects the persona's defined communication style
