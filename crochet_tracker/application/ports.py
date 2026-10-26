"""Ports the use cases depend on, so they know nothing of sqlite, PDFs or Qt (RF-3, RF-8, RF-13)."""

from pathlib import Path
from typing import Protocol, runtime_checkable

from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project


@runtime_checkable
class ProjectRepository(Protocol):
    """Stores projects and their notes and gives them back as domain objects."""

    def add(self, project: Project, now: int) -> int: ...

    def get(self, project_id: int) -> Project | None: ...

    def list_all(self) -> list[Project]: ...

    def save(self, project: Project, now: int) -> None: ...

    def delete_project(self, project_id: int) -> None: ...

    def add_note(self, project_id: int, note: Note) -> int: ...

    def list_notes(self, project_id: int) -> list[Note]: ...

    def save_note(self, note: Note) -> None: ...

    def delete_note(self, note_id: int) -> None: ...


@runtime_checkable
class GuideStore(Protocol):
    """Keeps a copy of each project's PDF, so the original can be moved or deleted (RF-8, RF-9)."""

    def copy(self, project_id: int, source: Path) -> str: ...

    def path(self, name: str | None) -> Path | None: ...


@runtime_checkable
class Clock(Protocol):
    """Seconds since the epoch; the unit the undo window is measured in (RF-16)."""

    def now(self) -> int: ...
