EM_DASH = "—"


def strip_em_dashes(text: str) -> str:
    """Replace em-dashes with a comma, matching Mira's persona style guide."""
    return text.replace(f" {EM_DASH} ", ", ").replace(EM_DASH, ", ")
