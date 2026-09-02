from datetime import timedelta

from src.cli.memory_commands import render_memory_debug, render_memory_timeline
from src.memory.models.memory import Memory, MemoryStatus, MemoryType, utcnow
from src.memory.retriever.scoring import ScoredMemory


def _make_memory(**overrides) -> Memory:
    defaults = dict(
        type=MemoryType.CAREER,
        subject="user",
        relation="works_at",
        value="Google",
        status=MemoryStatus.SUPERSEDED,
        importance=0.9,
        confidence=0.95,
        source_message_id="msg-1",
    )
    defaults.update(overrides)
    return Memory(**defaults)


def test_render_memory_timeline_empty_list():
    assert "No memories" in render_memory_timeline([])


def test_render_memory_timeline_groups_by_type_and_shows_supersede_chain():
    now = utcnow()
    google = _make_memory(valid_from=now - timedelta(days=200), status=MemoryStatus.SUPERSEDED)
    microsoft = _make_memory(value="Microsoft", status=MemoryStatus.ACTIVE, valid_from=now)

    output = render_memory_timeline([microsoft, google])

    assert "CAREER" in output
    assert "Google" in output
    assert "Microsoft" in output
    assert "SUPERSEDED" in output
    assert "ACTIVE" in output
    # Google (older) should appear before Microsoft (newer) in the output.
    assert output.index("Google") < output.index("Microsoft")


def test_render_memory_debug_empty_list():
    output = render_memory_debug([])
    assert "no retrieval" in output.lower()


def test_render_memory_debug_shows_all_score_components():
    memory = _make_memory(status=MemoryStatus.ACTIVE, value="Stripe interview tomorrow")
    scored = ScoredMemory(
        memory=memory,
        semantic_similarity=0.89,
        importance_weight=0.91,
        recency_weight=0.97,
        confidence_weight=0.95,
        final_score=0.93,
    )

    output = render_memory_debug([scored])

    assert "Stripe interview tomorrow" in output
    assert "0.89" in output
    assert "0.91" in output
    assert "0.97" in output
    assert "0.93" in output
