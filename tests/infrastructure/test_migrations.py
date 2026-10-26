import sqlite3

import pytest

from crochet_tracker.infrastructure import migrations
from crochet_tracker.infrastructure.migrations import (
    SCHEMA_VERSION,
    MigrationError,
    backup_path,
    current_version,
    migrate,
)


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "crochet.db"


@pytest.fixture
def connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


def test_a_fresh_database_is_brought_to_the_current_version(connection, db_path):
    migrate(connection, db_path)

    assert current_version(connection) == SCHEMA_VERSION
    tables = {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert {"project", "note"} <= tables


def test_an_old_database_keeps_its_data(connection, db_path):
    connection.execute("CREATE TABLE legacy (value TEXT)")
    connection.execute("INSERT INTO legacy VALUES ('no perder esto')")
    connection.commit()

    migrate(connection, db_path)

    assert current_version(connection) == SCHEMA_VERSION
    assert connection.execute("SELECT value FROM legacy").fetchone()[0] == "no perder esto"


def test_the_previous_file_is_kept_as_bak(connection, db_path):
    migrate(connection, db_path)

    backup = backup_path(db_path)
    assert backup.name == "crochet.db.bak"
    assert backup.is_file()
    with sqlite3.connect(backup) as old:
        assert current_version(old) == 0


def test_a_project_can_be_created_after_migrating(connection, db_path):
    migrate(connection, db_path)

    connection.execute(
        "INSERT INTO project (name, created_at, updated_at) VALUES (?, ?, ?)",
        ("Bufanda", 1_761_400_000, 1_761_400_000),
    )
    connection.commit()

    assert connection.execute("SELECT name FROM project").fetchone()[0] == "Bufanda"


def test_migrating_an_up_to_date_database_does_nothing(connection, db_path):
    migrate(connection, db_path)
    backup_path(db_path).unlink()

    migrate(connection, db_path)

    assert not backup_path(db_path).exists()


def test_a_failing_step_rolls_back_without_touching_the_data(
    connection, db_path, monkeypatch
):
    connection.execute("CREATE TABLE legacy (value TEXT)")
    connection.execute("INSERT INTO legacy VALUES ('intacto')")
    connection.commit()
    monkeypatch.setitem(
        migrations.MIGRATIONS, 0, ["CREATE TABLE half (x INTEGER)", "SELECT * FROM no_existe"]
    )

    with pytest.raises(sqlite3.Error):
        migrate(connection, db_path)

    assert current_version(connection) == 0
    assert connection.execute("SELECT value FROM legacy").fetchone()[0] == "intacto"
    tables = {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert "half" not in tables


def test_a_newer_database_is_refused(connection, db_path):
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")

    with pytest.raises(MigrationError):
        migrate(connection, db_path)
