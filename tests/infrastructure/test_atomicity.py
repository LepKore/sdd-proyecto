import sqlite3

import pytest

from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project
from crochet_tracker.infrastructure.sqlite_repository import SqliteProjectRepository

T0 = 1_761_400_000

MESSAGE = "disk I/O error"


class _FailingCommit(sqlite3.Connection):
    """A connection whose COMMIT always fails, like a full or busy disk (RF-13)."""

    def commit(self) -> None:
        raise sqlite3.OperationalError(MESSAGE)


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "crochet.db"


@pytest.fixture
def repository(db_path):
    return SqliteProjectRepository(db_path)


@pytest.fixture
def broken(db_path, monkeypatch):
    """A second repository on the same file where every write fails at COMMIT time."""

    def connect():
        # sqlite3.Connection is immutable, so commit() can only be overridden
        # in a subclass passed as factory.
        connection = sqlite3.connect(db_path, factory=_FailingCommit)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    repository = SqliteProjectRepository(db_path)
    monkeypatch.setattr(repository, "_connect", connect)
    return repository


def test_a_failed_save_keeps_the_last_saved_value(repository, broken):
    project_id = repository.add(Project("Bufanda"), T0)
    stored = repository.get(project_id)
    stored.rows_done = 3
    repository.save(stored, T0 + 1)

    stored.rows_done = 99
    with pytest.raises(sqlite3.OperationalError):
        broken.save(stored, T0 + 2)

    assert repository.get(project_id).rows_done == 3


def test_a_failed_insert_leaves_no_half_project(repository, broken, db_path):
    with pytest.raises(sqlite3.OperationalError):
        broken.add(Project("a medias"), T0)

    assert repository.list_all() == []


def test_a_failed_delete_keeps_the_project_its_notes_and_its_guide(
    repository, broken, tmp_path
):
    guides = tmp_path / "guides"
    guides.mkdir()
    guide = guides / "3-guide.pdf"
    guide.write_bytes(b"%PDF-1.7")
    project_id = repository.add(Project("completo", guide_file=guide.name), T0)
    repository.add_note(project_id, Note("una nota", T0))

    with pytest.raises(sqlite3.OperationalError):
        broken.delete_project(project_id)

    assert repository.get(project_id) is not None
    assert len(repository.list_notes(project_id)) == 1
    assert guide.is_file()
