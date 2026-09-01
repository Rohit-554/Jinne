from enum import StrEnum


class Verdict(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


def deterministic_check(response: str, expected_substring: str) -> Verdict:
    return Verdict.PASS if expected_substring.lower() in response.lower() else Verdict.FAIL
