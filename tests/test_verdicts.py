from src.evaluation.verdicts import Verdict, deterministic_check


def test_deterministic_check_passes_when_substring_present():
    assert deterministic_check("Your dog's name is Bruno!", "Bruno") == Verdict.PASS


def test_deterministic_check_is_case_insensitive():
    assert deterministic_check("your dog's name is bruno!", "Bruno") == Verdict.PASS


def test_deterministic_check_fails_when_substring_absent():
    assert deterministic_check("I don't know your dog's name.", "Bruno") == Verdict.FAIL


def test_deterministic_check_normalizes_non_breaking_hyphen():
    # Found via a live eval run: the model wrote "555‑5678" (non-breaking
    # hyphen) where the scenario expected a plain ASCII "555-5678" - a
    # correct answer that a naive substring check would score as FAIL.
    assert deterministic_check("Your current number is 555‑5678.", "555-5678") == Verdict.PASS


def test_deterministic_check_normalizes_en_and_em_dash():
    assert deterministic_check("It happened 2020–2021.", "2020-2021") == Verdict.PASS
    assert deterministic_check("Bruno — your dog — is great.", "Bruno - your dog") == Verdict.PASS
