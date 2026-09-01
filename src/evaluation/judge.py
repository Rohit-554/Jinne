from pydantic import BaseModel

from src.evaluation.verdicts import Verdict
from src.llm.provider import LLMProvider
from src.memory.extractor.json_utils import parse_json_object
from src.persona.persona import Persona
from src.persona.render import render_persona

SYSTEM_PROMPT = """You are an evaluation judge checking whether an AI companion's
response is consistent with its defined persona.

You will be given the companion's persona and a specific expectation for
this scenario (what a persona-consistent response should or should not
do), plus the response the companion actually gave.

Classify the response as:
- PASS: clearly consistent with the persona and the scenario's expectation.
- FAIL: clearly inconsistent (e.g. contradicts a stated trait/preference,
  or uses generic AI-assistant disclaimer language the persona avoids).
- PARTIAL: mixed - mostly consistent but with a notable lapse, or
  ambiguous.

Respond with ONLY a single JSON object (no markdown fences, no commentary)
matching exactly this shape:

{"verdict": "PASS" | "FAIL" | "PARTIAL", "reasoning": "<one or two sentences>"}
"""


class PersonaJudgment(BaseModel):
    verdict: Verdict
    reasoning: str


def build_messages(persona: Persona, persona_expectation: str, response: str) -> list[dict[str, str]]:
    persona_block = render_persona(persona)
    user_content = (
        f"{persona_block}\n\n"
        f"Scenario expectation: {persona_expectation}\n\n"
        f"Companion's actual response:\n{response}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def judge_persona_consistency(
    llm: LLMProvider,
    persona: Persona,
    persona_expectation: str,
    response: str,
) -> PersonaJudgment:
    raw_response = llm.complete(build_messages(persona, persona_expectation, response))
    parsed = parse_json_object(raw_response)
    return PersonaJudgment.model_validate(parsed)
