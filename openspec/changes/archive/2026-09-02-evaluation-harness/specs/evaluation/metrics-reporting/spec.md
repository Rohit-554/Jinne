## Purpose

Turn per-scenario verdicts into measured, reportable numbers and a durable failure record, so the project's evaluation claims are backed by actual results instead of impressions.

## ADDED Requirements

### Requirement: Per-Category and Overall Pass Rate
The system SHALL compute a pass rate per category and an overall pass rate, derived only from recorded scenario verdicts.

#### Scenario: Category pass rate reflects recorded verdicts
- **WHEN** metrics are computed after a run
- **THEN** each category's pass rate equals the count of PASS verdicts in that category divided by the number of scenarios run in that category

### Requirement: Written Results Report
The system SHALL write a results report file for each run, containing the per-category and overall metrics and the full list of scenario results.

#### Scenario: Report is written after a run
- **WHEN** an evaluation run completes
- **THEN** a report file is written containing the computed metrics and every scenario's result

### Requirement: Failure Detail Logging
For every scenario that did not receive a PASS verdict, the system SHALL log the scenario id, category, expected outcome, and actual response, so failures can be reviewed individually.

#### Scenario: Failed scenario detail is retrievable
- **WHEN** a scenario fails or is judged PARTIAL
- **THEN** its failure detail (id, category, expected outcome, actual response) is present in the run's output
