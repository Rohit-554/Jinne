import json

from src.evaluation.extraction_cases import ExpectedFact, ExtractionCase
from src.evaluation.extraction_metrics import CaseScore
from src.evaluation.extraction_report import run_extraction_metrics, write_extraction_report

EXTRACTION_SYSTEM_PREFIX = "You are the memory-extraction module"


class FakeLLMProvider:
    def __init__(self, response_by_message: dict[str, str]):
        self._response_by_message = response_by_message

    def complete(self, messages: list[dict[str, str]]) -> str:
        assert messages[0]["content"].startswith(EXTRACTION_SYSTEM_PREFIX)
        user_message = messages[-1]["content"]
        return self._response_by_message[user_message]


def test_run_extraction_metrics_calls_real_extractor_per_case():
    cases = [
        ExtractionCase(
            id="c1",
            message="My dog's name is Bruno.",
            expected=[ExpectedFact(relation="pet_name", value="Bruno")],
        ),
        ExtractionCase(id="c2", message="hi", expected=[]),
    ]
    provider = FakeLLMProvider(
        {
            "My dog's name is Bruno.": """{
                "candidates": [{
                    "decision": "SAVE", "type": "RELATIONSHIP", "subject": "user",
                    "relation": "pet_name", "value": "Bruno",
                    "importance": 0.8, "confidence": 0.95
                }]
            }""",
            "hi": '{"candidates": []}',
        }
    )

    scores = run_extraction_metrics(cases, provider)

    assert len(scores) == 2
    assert scores[0].true_positives == ["Bruno"]
    assert scores[1].true_positives == []
    assert scores[1].false_positives == []


def test_write_extraction_report_round_trips(tmp_path):
    scores = [
        CaseScore(case_id="c1", true_positives=["Bruno"], false_positives=[], false_negatives=[]),
        CaseScore(case_id="c2", true_positives=[], false_positives=["extra"], false_negatives=["missed"]),
    ]

    report_path = write_extraction_report(scores, results_dir=tmp_path)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["precision_recall"]["true_positive_count"] == 1
    assert payload["precision_recall"]["false_positive_count"] == 1
    assert payload["precision_recall"]["false_negative_count"] == 1
    assert len(payload["case_scores"]) == 2
