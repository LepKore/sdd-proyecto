"""sqlite persistence for projects (RF-1, RF-2, RF-3, RF-4, RF-5, RF-10, RF-11, RF-12)."""

import sqlite3
from contextlib import closing
from pathlib import Path

from crochet_tracker.domain.project import Project
from crochet_tracker.infrastructure.migrations import migrate

_COLUMNS = (
    "name, is_finished, rows_done, knots_done, guide_page, guide_file, created_at, updated_at"
)


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


class SqliteProjectRepository:
    """One connection per operation: no shared state to keep in sync."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
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

    def add(self, project: Project, now: int) -> int:
        """Insert the project and return its new id."""
        with closing(self._connect()) as connection, connection:
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
        with closing(self._connect()) as connection, connection:
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
