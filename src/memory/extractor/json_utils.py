import json
import re

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


class JsonExtractionError(ValueError):
    pass


def parse_json_object(text: str) -> dict:
    candidate = _CODE_FENCE_RE.sub("", text).strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(candidate[start : end + 1])
        except json.JSONDecodeError:
            pass

    raise JsonExtractionError(f"Could not parse a JSON object from LLM output: {text!r}")
