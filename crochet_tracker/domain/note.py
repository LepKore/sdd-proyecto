"""Note rules (RF-14, RF-15)."""

from dataclasses import dataclass

from crochet_tracker.domain.errors import EmptyNoteText


def validate_body(body: str) -> str:
    """Return the body unchanged, or raise EmptyNoteText if it has no visible text (CL-19).

    Only emptiness is checked: a note is free text, so edges are not trimmed.
    """
    if not body.strip():
        raise EmptyNoteText("note text must not be empty or blank")
    return body


@dataclass
class Note:
    """A free-text note; its creation time is set once and kept when edited (RF-15)."""

    body: str
    created_at: int
    id: int | None = None

    def __post_init__(self) -> None:
        self.body = validate_body(self.body)

    def edit(self, body: str) -> None:
        self.body = validate_body(body)
