## Purpose

Provide a repeatable, versioned set of conversation scenarios covering the behaviors the companion is meant to prove - recall, updates, temporal reasoning, and persona consistency - so the system can be measured the same way every time instead of judged by ad hoc demo runs.

## ADDED Requirements

### Requirement: Scenario Categories
The dataset SHALL include scenarios in five categories: factual recall, long-range recall, contradiction/update, temporal reasoning, and persona consistency, with at least ten scenarios per category.

#### Scenario: Dataset covers all five categories
- **WHEN** the scenario dataset is loaded
- **THEN** each of the five categories has at least ten scenarios

### Requirement: Scenario Structure
Each scenario SHALL specify: a unique id, its category, an ordered list of conversation turns to send before the final question, a final question, and an expected outcome usable to check the response (an expected substring/fact for deterministic categories, or a persona expectation for the persona-consistency category).

#### Scenario: Scenario has required fields
- **WHEN** a scenario is loaded from the dataset
- **THEN** it has an id, category, turns, a final question, and an expected outcome

### Requirement: Long-Range Scenario Spacing
Long-range recall scenarios SHALL separate the fact-establishing turn from the final question by multiple intervening turns, so they exercise recall across a longer conversation rather than the immediately preceding message.

#### Scenario: Long-range scenario has spacing
- **WHEN** a long-range recall scenario is loaded
- **THEN** at least several unrelated turns appear between the turn that establishes the fact and the final question
