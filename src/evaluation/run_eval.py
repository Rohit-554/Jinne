import time

from src.config import get_env, load_config
from src.evaluation.evaluate import evaluate_scenario
from src.evaluation.metrics import compute_metrics
from src.evaluation.report import write_report
from src.evaluation.results import ScenarioResult
from src.evaluation.scenarios import Scenario, load_scenarios
from src.evaluation.verdicts import Verdict
from src.llm.fastembed_provider import FastEmbedProvider
from src.llm.groq_provider import GroqProvider
from src.llm.provider import EmbeddingProvider, LLMProvider

SCENARIOS_PATH = "eval/scenarios/scenarios.jsonl"


def _evaluate_or_record_error(scenario: Scenario, llm: LLMProvider, embedder: EmbeddingProvider) -> ScenarioResult:
    try:
        return evaluate_scenario(scenario, llm, embedder)
    except Exception as exc:
        expected = scenario.expected_substring or scenario.persona_expectation or ""
        return ScenarioResult(
            scenario_id=scenario.id,
            category=scenario.category,
            verdict=Verdict.FAIL,
            response=f"ERROR: {exc!r}",
            expected=expected,
        )


def main() -> None:
    load_config()
    groq_api_key = get_env("GROQ_API_KEY", required=True)
    groq_model = get_env("GROQ_MODEL", default="openai/gpt-oss-120b")
    embedding_model = get_env("EMBEDDING_MODEL", default="BAAI/bge-small-en-v1.5")

    llm = GroqProvider(api_key=groq_api_key, model=groq_model)
    embedder = FastEmbedProvider(model_name=embedding_model)

    scenarios = load_scenarios(SCENARIOS_PATH)
    print(f"Running {len(scenarios)} scenarios...")

    results: list[ScenarioResult] = []
    for i, scenario in enumerate(scenarios, start=1):
        start = time.monotonic()
        result = _evaluate_or_record_error(scenario, llm, embedder)
        elapsed = time.monotonic() - start
        print(f"  [{i}/{len(scenarios)}] {scenario.id} ({scenario.category.value}): {result.verdict.value} ({elapsed:.1f}s)")
        results.append(result)

    report_path = write_report(results)
    metrics = compute_metrics(results)

    print()
    print(
        f"Overall: {metrics.overall.pass_rate:.0%} pass, "
        f"{metrics.overall.partial_rate:.0%} partial, "
        f"{metrics.overall.fail_rate:.0%} fail "
        f"({metrics.overall.total} scenarios)"
    )
    for category, cat_metrics in metrics.by_category.items():
        print(f"  {category.value}: {cat_metrics.pass_rate:.0%} pass ({cat_metrics.total} scenarios)")
    print(f"\nReport written to {report_path}")


if __name__ == "__main__":
    main()
