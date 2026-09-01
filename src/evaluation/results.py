from pydantic import BaseModel

from src.evaluation.scenarios import ScenarioCategory
from src.evaluation.verdicts import Verdict


class ScenarioResult(BaseModel):
    scenario_id: str
    category: ScenarioCategory
    verdict: Verdict
    response: str
    expected: str
    reasoning: str | None = None
