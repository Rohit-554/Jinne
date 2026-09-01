from src.persona.persona import Persona, load_persona
from src.persona.render import render_persona


def test_load_persona_returns_a_persona_without_error():
    persona = load_persona()

    assert isinstance(persona, Persona)
    assert persona.name
    assert persona.traits
    assert persona.communication_style
    assert persona.stable_preferences


def test_render_persona_includes_name_traits_and_style():
    persona = load_persona()

    rendered = render_persona(persona)

    assert persona.name in rendered
    for trait in persona.traits:
        assert trait in rendered
    for style in persona.communication_style:
        assert style in rendered
    for preference in persona.stable_preferences:
        assert preference in rendered
