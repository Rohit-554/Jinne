from src.evaluation.verdicts import Verdict, deterministic_check


def test_deterministic_check_passes_when_substring_present():
    assert deterministic_check("Your dog's name is Bruno!", "Bruno") == Verdict.PASS


def test_deterministic_check_is_case_insensitive():
    assert deterministic_check("your dog's name is bruno!", "Bruno") == Verdict.PASS


def test_deterministic_check_fails_when_substring_absent():
    assert deterministic_check("I don't know your dog's name.", "Bruno") == Verdict.FAIL
