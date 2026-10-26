"""Versioned schema and migration (constitution, section 5).

`user_version` in the database header says which schema it has. Each step runs
inside one transaction: either the whole step lands with its version bump, or
nothing does. The previous file is kept as `crochet.db.bak` before touching it.
"""

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 1


class MigrationError(Exception):
    """The database cannot be migrated by this version of the application."""


SCHEMA_V1 = [
    """
    CREATE TABLE project (
        id            INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL,
        is_finished   INTEGER NOT NULL DEFAULT 0,
        rows_done     INTEGER NOT NULL DEFAULT 0,
        knots_done    INTEGER NOT NULL DEFAULT 0,
        guide_page    INTEGER NOT NULL DEFAULT 1,
        guide_file    TEXT,
        created_at    INTEGER NOT NULL,
        updated_at    INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE note (
        id          INTEGER PRIMARY KEY,
        project_id  INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
        body        TEXT    NOT NULL,
        created_at  INTEGER NOT NULL
    )
    """,
    "CREATE INDEX idx_project_updated ON project(updated_at DESC, id DESC)",
    "CREATE INDEX idx_note_project ON note(project_id, created_at DESC, id DESC)",
]

# MIGRATIONS[from_version] holds the statements that reach from_version + 1.
MIGRATIONS: dict[int, list[str]] = {0: SCHEMA_V1}


def current_version(connection: sqlite3.Connection) -> int:
    return connection.execute("PRAGMA user_version").fetchone()[0]


def backup_path(db_path: Path) -> Path:
    return db_path.with_name(db_path.name + ".bak")


def migrate(connection: sqlite3.Connection, db_path: Path) -> None:
    """Bring the database up to SCHEMA_VERSION, keeping a copy of the previous file."""
    version = current_version(connection)
    if version > SCHEMA_VERSION:
        raise MigrationError(
            f"database schema version {version} is newer than {SCHEMA_VERSION}"
        )
    if version == SCHEMA_VERSION:
        return

    # The backup API reads through the WAL, so the copy is consistent even if
    # the database is in WAL mode and the file on disk is not up to date.
    backup_connection = sqlite3.connect(backup_path(db_path))
    try:
        connection.backup(backup_connection)
    finally:
        backup_connection.close()

    for from_version in range(version, SCHEMA_VERSION):
        # BEGIN is explicit: Python's sqlite3 does not open a transaction for
        # DDL, and a half-created table would survive a ROLLBACK.
        connection.commit()
        connection.execute("BEGIN")
        try:
            for statement in MIGRATIONS[from_version]:
                connection.execute(statement)
            connection.execute(f"PRAGMA user_version = {from_version + 1}")
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
