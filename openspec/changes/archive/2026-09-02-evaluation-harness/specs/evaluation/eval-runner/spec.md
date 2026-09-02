## Purpose

Replay each scenario through the real conversation system - not a mock - and produce a verdict per scenario, so evaluation results reflect what the shipped system actually does.

## ADDED Requirements

### Requirement: End-to-End Scenario Execution
For each scenario, the runner SHALL create an isolated conversation engine and memory store, send the scenario's turns in order through the real `ConversationEngine`, then send the final question and capture the response.

#### Scenario: Scenario runs against a fresh store
- **WHEN** a scenario is executed
- **THEN** it uses a memory store containing only the memories produced by that scenario's own turns, not memories from any other scenario

### Requirement: Deterministic Verdicts for Factual Categories
For factual recall, long-range recall, contradiction/update, and temporal reasoning scenarios, the runner SHALL determine PASS or FAIL by checking whether the expected fact is present in the response, without an LLM-judge call.

#### Scenario: Expected fact present passes
- **WHEN** a factual-category scenario's response contains its expected fact
- **THEN** the scenario is recorded as PASS

#### Scenario: Expected fact absent fails
- **WHEN** a factual-category scenario's response does not contain its expected fact
- **THEN** the scenario is recorded as FAIL

### Requirement: LLM-Judge Verdicts for Persona Consistency
For persona consistency scenarios, the runner SHALL use an LLM-as-judge to classify the response as PASS, FAIL, or PARTIAL against the persona's defined traits, and SHALL record the judge's stated reasoning alongside the verdict.

#### Scenario: Persona-consistent response passes
- **WHEN** a persona consistency scenario's response is consistent with the defined persona
- **THEN** the judge records a PASS verdict with its reasoning

### Requirement: Per-Scenario Result Record
The runner SHALL record, for every scenario, its id, category, verdict, the actual response, and the expected outcome, regardless of whether it passed.

#### Scenario: Result record captures actual vs expected
- **WHEN** a scenario finishes running
- **THEN** its result record includes the response the system actually produced and the outcome that was expected
