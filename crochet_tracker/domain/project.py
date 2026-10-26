"""Project name rules (RF-1, RF-4)."""

from crochet_tracker.domain.errors import InvalidProjectName

MAX_NAME_LENGTH = 100


def normalize_name(name: str) -> str:
    """Return the name with its edges trimmed, or raise InvalidProjectName.

    Only the edges are trimmed: whatever is left is kept as typed (CL-2).
    Repeated names are allowed; uniqueness is not the domain's business (CL-4, CL-6).
    """
    trimmed = name.strip()
    if not trimmed:
        raise InvalidProjectName("project name must not be empty or blank")
    if len(trimmed) > MAX_NAME_LENGTH:
        raise InvalidProjectName(f"project name must be at most {MAX_NAME_LENGTH} characters")
    return trimmed
