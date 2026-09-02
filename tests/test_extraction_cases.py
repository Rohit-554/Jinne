import json

from src.evaluation.extraction_cases import load_extraction_cases


def test_load_extraction_cases_reads_jsonl_fixture(tmp_path):
    fixture = tmp_path / "cases.jsonl"
    records = [
        {
            "id": "save-1",
            "message": "Pizza has been my favourite food since childhood.",
            "expected": [{"relation": "favourite_food", "value": "Pizza"}],
        },
        {
            "id": "ignore-1",
            "message": "I'm eating pizza right now.",
            "expected": [],
        },
    ]
    fixture.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    cases = load_extraction_cases(fixture)

    assert len(cases) == 2
    assert cases[0].id == "save-1"
    assert cases[0].expected[0].value == "Pizza"
    assert cases[1].expected == []


def test_load_extraction_cases_skips_blank_lines(tmp_path):
    fixture = tmp_path / "cases.jsonl"
    record = {"id": "x", "message": "hi", "expected": []}
    fixture.write_text(f"\n{json.dumps(record)}\n\n", encoding="utf-8")

    cases = load_extraction_cases(fixture)

    assert len(cases) == 1
