## ADDED Requirements

### Requirement: Pluggable Conversation System
The runner SHALL support executing a scenario against any conversation system supplied via a pluggable factory, so the same scenario dataset and end-to-end execution logic can evaluate the proposed system or an alternative baseline system without duplicating the runner itself.

#### Scenario: Same runner drives a different system
- **WHEN** the runner is given a factory that builds a baseline conversation engine instead of the proposed system's engine
- **THEN** the scenario's turns and final question are still sent in order and a response is still captured, without any change to the runner's own code
