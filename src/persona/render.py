from src.persona.persona import Persona


def render_persona(persona: Persona) -> str:
    traits = ", ".join(persona.traits)
    style = ", ".join(persona.communication_style)
    preferences = ", ".join(persona.stable_preferences)
    return (
        f"PERSONA\n"
        f"{persona.name} is {traits}.\n"
        f"Communication style: {style}.\n"
        f"Stable preferences: {preferences}."
    )
