# Comparison Reporting Specification

## Purpose

Turn per-system scenario results into a side-by-side comparison, so the value (or lack of value) of the proposed system's architecture over simpler baselines is a measured claim, not an assumed one.

## Requirements

### Requirement: Same Scenarios, Multiple Systems
The system SHALL run the full scenario dataset against the proposed system, Baseline A, and Baseline B, using the same grading logic (deterministic checks and persona judge) for every system.

#### Scenario: All three systems graded identically
- **WHEN** the comparison is run
- **THEN** each system's results for a given scenario are produced by the same verdict logic used for that scenario's category

### Requirement: Comparative Report
The system SHALL produce a report showing each system's per-category and overall pass rate side by side, derived only from that run's actual results.

#### Scenario: Report shows all three systems per category
- **WHEN** the comparison report is generated
- **THEN** it includes, for every category, the pass rate achieved by the proposed system, Baseline A, and Baseline B
