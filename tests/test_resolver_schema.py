import pytest
from pydantic import ValidationError

from src.memory.resolver.schemas import ResolverAction, ResolverDecision


def test_supersede_requires_superseded_memory_id():
    with pytest.raises(ValidationError):
        ResolverDecision(action=ResolverAction.SUPERSEDE)


def test_duplicate_requires_superseded_memory_id():
    with pytest.raises(ValidationError):
        ResolverDecision(action=ResolverAction.DUPLICATE)


def test_independent_does_not_require_superseded_memory_id():
    decision = ResolverDecision(action=ResolverAction.INDEPENDENT)
    assert decision.superseded_memory_id is None


def test_supersede_with_id_is_valid():
    decision = ResolverDecision(action=ResolverAction.SUPERSEDE, superseded_memory_id=7)
    assert decision.superseded_memory_id == 7
