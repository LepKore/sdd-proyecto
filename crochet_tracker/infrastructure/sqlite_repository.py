"""sqlite persistence for projects and notes (RF-1..RF-6, RF-10..RF-15)."""

import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path

from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project
from crochet_tracker.infrastructure.app_paths import GUIDES_DIR_NAME
from crochet_tracker.infrastructure.migrations import migrate

_COLUMNS = (
    "name, is_finished, rows_done, knots_done, guide_page, guide_file, created_at, updated_at"
)
_NOTE_COLUMNS = "body, created_at"


def _to_project(row: sqlite3.Row) -> Project:
    return Project(
        id=row["id"],
        name=row["name"],
        rows_done=row["rows_done"],
        knots_done=row["knots_done"],
        is_finished=bool(row["is_finished"]),
        guide_page=row["guide_page"],
        guide_file=row["guide_file"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _to_note(row: sqlite3.Row) -> Note:
    return Note(body=row["body"], created_at=row["created_at"], id=row["id"])


class SqliteProjectRepository:
    """One connection per operation: no shared state to keep in sync."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._guides_dir = db_path.parent / GUIDES_DIR_NAME
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            migrate(connection, db_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = FULL")
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _write(self) -> Iterator[sqlite3.Connection]:
        """Commit here, explicitly: sqlite3's own ``__exit__`` commits in C,
        bypassing any Python override, which made a failing COMMIT impossible
        to reproduce in a test (RF-13)."""
        with closing(self._connect()) as connection:
            try:
                yield connection
            except BaseException:
                connection.rollback()
                raise
            connection.commit()

    def add(self, project: Project, now: int) -> int:
        """Insert the project and return its new id."""
        with self._write() as connection:
            cursor = connection.execute(
                f"INSERT INTO project ({_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    project.name,
                    int(project.is_finished),
                    project.rows_done,
                    project.knots_done,
                    project.guide_page,
                    project.guide_file,
                    now,
                    now,
                ),
            )
            return cursor.lastrowid

    def get(self, project_id: int) -> Project | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                f"SELECT id, {_COLUMNS} FROM project WHERE id = ?", (project_id,)
            ).fetchone()
        return _to_project(row) if row else None

    def list_all(self) -> list[Project]:
        """Most recently modified first; opening a project does not reorder (RF-2)."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                f"SELECT id, {_COLUMNS} FROM project ORDER BY updated_at DESC, id DESC"
            ).fetchall()
        return [_to_project(row) for row in rows]

    def save(self, project: Project, now: int) -> None:
        """Write every mutable field and bump updated_at (RF-13)."""
        with self._write() as connection:
            connection.execute(
                "UPDATE project SET name = ?, is_finished = ?, rows_done = ?, knots_done = ?,"
                " guide_page = ?, guide_file = ?, updated_at = ? WHERE id = ?",
                (
                    project.name,
                    int(project.is_finished),
                    project.rows_done,
                    project.knots_done,
                    project.guide_page,
                    project.guide_file,
                    now,
                    project.id,
                ),
            )

    def delete_project(self, project_id: int) -> None:
        """Remove the project, its notes (cascade) and its copied guide (RF-6)."""
        project = self.get(project_id)
        if project is None:
            return
        with self._write() as connection:
            connection.execute("DELETE FROM project WHERE id = ?", (project_id,))
        if project.guide_file:
            # Only the file name is stored; keep it inside the guides folder.
            (self._guides_dir / Path(project.guide_file).name).unlink(missing_ok=True)

    def add_note(self, project_id: int, note: Note) -> int:
        """Insert the note and return its new id."""
        with self._write() as connection:
            cursor = connection.execute(
                "INSERT INTO note (project_id, body, created_at) VALUES (?, ?, ?)",
                (project_id, note.body, note.created_at),
            )
            return cursor.lastrowid

    def list_notes(self, project_id: int) -> list[Note]:
        """Newest first (RF-14)."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                f"SELECT id, {_NOTE_COLUMNS} FROM note WHERE project_id = ?"
                " ORDER BY created_at DESC, id DESC",
                (project_id,),
            ).fetchall()
        return [_to_note(row) for row in rows]

    def save_note(self, note: Note) -> None:
        """Only the text changes; the creation time is kept (RF-15)."""
        with self._write() as connection:
            connection.execute("UPDATE note SET body = ? WHERE id = ?", (note.body, note.id))

    def delete_note(self, note_id: int) -> None:
        with self._write() as connection:
            connection.execute("DELETE FROM note WHERE id = ?", (note_id,))
