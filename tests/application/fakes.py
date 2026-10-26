"""In-memory doubles for the application tests: no sqlite, no Qt, no PDFs (T19)."""

from dataclasses import replace
from pathlib import Path

from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project


class FakeClock:
    """A clock the test moves by hand, so time never makes a test flaky."""

    def __init__(self, now: int = 1_000) -> None:
        self._now = now

    def now(self) -> int:
        return self._now

    def advance(self, seconds: int) -> None:
        self._now += seconds


class FakeRepository:
    """Stores copies, like the real one: whatever the view does in memory stays there."""

    def __init__(self) -> None:
        self.projects: dict[int, Project] = {}
        self.notes: dict[int, tuple[int, Note]] = {}
        self.fail_on_save = False
        self.saves = 0
        self._next_id = 1

    def add(self, project: Project, now: int) -> int:
        project_id = self._take_id()
        self.projects[project_id] = replace(
            project, id=project_id, created_at=now, updated_at=now
        )
        return project_id

    def get(self, project_id: int) -> Project | None:
        stored = self.projects.get(project_id)
        return replace(stored) if stored else None

    def list_all(self) -> list[Project]:
        newest_first = sorted(
            self.projects.values(), key=lambda p: (p.updated_at, p.id), reverse=True
        )
        return [replace(project) for project in newest_first]

    def save(self, project: Project, now: int) -> None:
        if self.fail_on_save:
            raise RuntimeError("disk I/O error")
        self.saves += 1
        self.projects[project.id] = replace(project, updated_at=now)

    def delete_project(self, project_id: int) -> None:
        self.projects.pop(project_id, None)
        self.notes = {
            note_id: entry for note_id, entry in self.notes.items() if entry[0] != project_id
        }

    def add_note(self, project_id: int, note: Note) -> int:
        note_id = self._take_id()
        self.notes[note_id] = (project_id, replace(note, id=note_id))
        return note_id

    def list_notes(self, project_id: int) -> list[Note]:
        newest_first = sorted(
            (note for owner, note in self.notes.values() if owner == project_id),
            key=lambda n: (n.created_at, n.id),
            reverse=True,
        )
        return [replace(note) for note in newest_first]

    def save_note(self, note: Note) -> None:
        owner = self.notes[note.id][0]
        self.notes[note.id] = (owner, replace(note))

    def delete_note(self, note_id: int) -> None:
        self.notes.pop(note_id, None)

    def _take_id(self) -> int:
        new_id = self._next_id
        self._next_id += 1
        return new_id


class FakeGuideStore:
    """Holds the copied bytes in memory; it never touches disk."""

    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    def copy(self, project_id: int, source: Path) -> str:
        name = f"{project_id}-{len(self.files) + 1}.pdf"
        self.files[name] = source.read_bytes()
        return name

    def path(self, name: str | None) -> Path | None:
        # shortcut: T19 only needs the shape of the port; real paths arrive with T24's tests.
        return None
