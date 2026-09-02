from src.evaluation.judge import judge_persona_consistency
from src.evaluation.results import ScenarioResult
from src.evaluation.runner import EngineFactory, proposed_system_factory, run_scenario
from src.evaluation.scenarios import Scenario, ScenarioCategory
from src.evaluation.verdicts import deterministic_check
from src.llm.provider import EmbeddingProvider, LLMProvider
from src.persona.persona import DEFAULT_PERSONA


def evaluate_scenario(
    scenario: Scenario,
    llm: LLMProvider,
    embedder: EmbeddingProvider,
    engine_factory: EngineFactory = proposed_system_factory,
) -> ScenarioResult:
    response, store = run_scenario(scenario, llm, embedder, engine_factory=engine_factory)
    store.close()

    if scenario.category == ScenarioCategory.PERSONA_CONSISTENCY:
        judgment = judge_persona_consistency(llm, DEFAULT_PERSONA, scenario.persona_expectation, response)
        return ScenarioResult(
            scenario_id=scenario.id,
            category=scenario.category,
            verdict=judgment.verdict,
            response=response,
            expected=scenario.persona_expectation,
            reasoning=judgment.reasoning,
        )

    verdict = deterministic_check(response, scenario.expected_substring)
    return ScenarioResult(
        scenario_id=scenario.id,
        category=scenario.category,
        verdict=verdict,
        response=response,
        expected=scenario.expected_substring,
    )
