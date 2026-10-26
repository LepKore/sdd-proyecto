"""Project entity: name, counters and finished state (RF-1, RF-4, RF-5, RF-11, RF-12)."""

from dataclasses import dataclass

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


@dataclass
class Project:
    """A crochet project in progress.

    Counters are independent, never drop below zero and have no upper bound
    (CL-17, CL-18). Counting on a finished project does not change its state (CL-28).
    """

    name: str
    rows_done: int = 0
    knots_done: int = 0
    is_finished: bool = False

    def __post_init__(self) -> None:
        self.name = normalize_name(self.name)

    def change_rows(self, delta: int) -> None:
        self.rows_done = max(0, self.rows_done + delta)

    def change_knots(self, delta: int) -> None:
        self.knots_done = max(0, self.knots_done + delta)

    def toggle_finished(self) -> None:
        self.is_finished = not self.is_finished
