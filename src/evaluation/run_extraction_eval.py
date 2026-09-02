from src.config import get_env, load_config
from src.evaluation.extraction_cases import load_extraction_cases
from src.evaluation.extraction_metrics import aggregate_precision_recall
from src.evaluation.extraction_report import run_extraction_metrics, write_extraction_report
from src.llm.groq_provider import GroqProvider

CASES_PATH = "eval/scenarios/extraction_cases.jsonl"


def main() -> None:
    load_config()
    groq_api_key = get_env("GROQ_API_KEY", required=True)
    groq_model = get_env("GROQ_MODEL", default="openai/gpt-oss-120b")
    llm = GroqProvider(api_key=groq_api_key, model=groq_model)

    cases = load_extraction_cases(CASES_PATH)
    print(f"Running {len(cases)} extraction cases...")

    scores = run_extraction_metrics(cases, llm)
    for score in scores:
        status = "OK" if not score.false_positives and not score.false_negatives else "MISS"
        print(f"  {score.case_id}: {status} (TP={len(score.true_positives)} FP={len(score.false_positives)} FN={len(score.false_negatives)})")

    precision_recall = aggregate_precision_recall(scores)
    report_path = write_extraction_report(scores)

    print()
    print(
        f"Precision: {precision_recall.precision:.0%} "
        f"({precision_recall.true_positive_count}/{precision_recall.true_positive_count + precision_recall.false_positive_count})"
    )
    print(
        f"Recall: {precision_recall.recall:.0%} "
        f"({precision_recall.true_positive_count}/{precision_recall.true_positive_count + precision_recall.false_negative_count})"
    )
    print(f"\nReport written to {report_path}")


if __name__ == "__main__":
    main()
