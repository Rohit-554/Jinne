from enum import StrEnum

# LLM output often uses "smart" Unicode punctuation (non-breaking hyphens,
# en/em dashes, minus signs, non-breaking spaces) where a plain ASCII
# equivalent is expected. Normalize both sides before comparing so a
# typographically different but factually correct answer isn't scored
# as a false negative.
_PUNCTUATION_NORMALIZATION = str.maketrans(
    {
        "‐": "-",  # hyphen
        "‑": "-",  # non-breaking hyphen
        "‒": "-",  # figure dash
        "–": "-",  # en dash
        "—": "-",  # em dash
        "−": "-",  # minus sign
        " ": " ",  # non-breaking space
        " ": " ",  # narrow no-break space
    }
)


class Verdict(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


def _normalize(text: str) -> str:
    return text.translate(_PUNCTUATION_NORMALIZATION).lower()


def deterministic_check(response: str, expected_substring: str) -> Verdict:
    return Verdict.PASS if _normalize(expected_substring) in _normalize(response) else Verdict.FAIL
