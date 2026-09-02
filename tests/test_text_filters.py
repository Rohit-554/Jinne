from src.chat.text_filters import strip_em_dashes


def test_strip_em_dashes_replaces_spaced_em_dash():
    assert strip_em_dashes("curiosities — someone asks") == "curiosities, someone asks"


def test_strip_em_dashes_replaces_unspaced_em_dash():
    assert strip_em_dashes("Nope—my circuits can't handle it") == "Nope, my circuits can't handle it"


def test_strip_em_dashes_leaves_text_without_em_dashes_unchanged():
    assert strip_em_dashes("Hi, how are you today?") == "Hi, how are you today?"


def test_strip_em_dashes_handles_multiple_occurrences():
    assert strip_em_dashes("one—two—three") == "one, two, three"
