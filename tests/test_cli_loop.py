import io

from src.cli.main import run


class FakeEngine:
    def __init__(self):
        self.received_messages: list[str] = []

    def handle_message(self, user_message: str) -> str:
        self.received_messages.append(user_message)
        return f"echo: {user_message}"


def test_run_starts_processes_a_turn_and_exits_cleanly():
    engine = FakeEngine()
    input_stream = io.StringIO("hello there\n/exit\n")
    output_stream = io.StringIO()

    run(engine=engine, input_stream=input_stream, output_stream=output_stream)

    assert engine.received_messages == ["hello there"]
    output = output_stream.getvalue()
    assert "Type /exit to quit" in output
    assert "echo: hello there" in output


def test_run_exits_cleanly_on_empty_input_stream():
    engine = FakeEngine()
    input_stream = io.StringIO("")
    output_stream = io.StringIO()

    run(engine=engine, input_stream=input_stream, output_stream=output_stream)

    assert engine.received_messages == []


class FlakyEngine:
    """Raises on the first turn, then behaves normally - simulates a
    transient failure (network blip, malformed LLM output) that should
    not kill the whole session."""

    def __init__(self):
        self.calls = 0

    def handle_message(self, user_message: str) -> str:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("simulated transient failure")
        return f"echo: {user_message}"


def test_run_survives_a_failed_turn_and_keeps_the_session_going():
    engine = FlakyEngine()
    input_stream = io.StringIO("this one will fail\nthis one should work\n/exit\n")
    output_stream = io.StringIO()

    run(engine=engine, input_stream=input_stream, output_stream=output_stream)

    assert engine.calls == 2
    output = output_stream.getvalue()
    assert "something went wrong" in output
    assert "echo: this one should work" in output
