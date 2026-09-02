## Purpose

Measure the memory extractor's own precision and recall against labeled ground truth, independent of end-to-end conversation grading, so a wrong final answer elsewhere in the pipeline can't be mistaken for (or hide) an extraction problem.

## ADDED Requirements

### Requirement: Labeled Extraction Ground Truth
The dataset SHALL pair each input message with the set of relation+value facts that should be extracted (a SAVE decision), which SHALL be empty for a message that should be entirely ignored.

#### Scenario: IGNORE case has an empty expected set
- **WHEN** a ground-truth case represents a message that should not produce any memory
- **THEN** its expected set of facts is empty

#### Scenario: Multi-fact case lists every expected fact
- **WHEN** a ground-truth case represents a message containing multiple memory-worthy facts
- **THEN** its expected set includes every fact that should be extracted from it

### Requirement: Live Extraction Against Ground Truth
The evaluator SHALL run the real memory extractor (not a mock) against each case's message and record the actual SAVE candidates it produces.

#### Scenario: Evaluator uses the real extractor
- **WHEN** the extraction metrics evaluator runs
- **THEN** each case's actual candidates come from a live call to the extractor, not a canned response

### Requirement: Precision and Recall Computation
The system SHALL compute precision and recall by matching actual SAVE candidates against expected facts primarily by value (case-insensitive substring match in either direction), not by requiring an exact relation-string match, since reasonable relation-naming choices can vary between extraction calls without the extracted fact being wrong. Unmatched actual candidates count as false positives; unmatched expected facts count as false negatives.

#### Scenario: Correct single-fact extraction counts as a true positive
- **WHEN** the actual SAVE candidates for a case exactly match its expected facts
- **THEN** every expected fact counts as a true positive and no false positives or false negatives are recorded for that case

#### Scenario: Missed fact counts as a false negative
- **WHEN** an expected fact has no matching actual candidate
- **THEN** it counts as a false negative

#### Scenario: Extra or incorrect extraction counts as a false positive
- **WHEN** an actual SAVE candidate has no matching expected fact
- **THEN** it counts as a false positive

### Requirement: Reported Metrics Are Real
The written report SHALL state precision and recall computed strictly from the recorded true positive, false positive, and false negative counts, with no invented or adjusted values.

#### Scenario: Metrics derive only from recorded counts
- **WHEN** the extraction metrics report is generated
- **THEN** precision equals `TP / (TP + FP)` and recall equals `TP / (TP + FN)` using only counts from cases that were actually run
