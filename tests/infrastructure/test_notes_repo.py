import sqlite3

import pytest

from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project
from crochet_tracker.infrastructure.sqlite_repository import SqliteProjectRepository

T0 = 1_761_400_000


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "crochet.db"


@pytest.fixture
def repository(db_path):
    return SqliteProjectRepository(db_path)


@pytest.fixture
def project_id(repository):
    return repository.add(Project("Bufanda"), T0)


def add(repository, project_id, body, created_at=T0):
    note = Note(body, created_at)
    note.id = repository.add_note(project_id, note)
    return note


def test_adding_a_note_stores_it_with_its_creation_time(repository, project_id):
    add(repository, project_id, "primera vuelta")

    notes = repository.list_notes(project_id)

    assert len(notes) == 1
    assert notes[0].id is not None
    assert notes[0].body == "primera vuelta"
    assert notes[0].created_at == T0


def test_notes_come_newest_first(repository, project_id):
    add(repository, project_id, "vieja", created_at=T0)
    add(repository, project_id, "media", created_at=T0 + 10)
    add(repository, project_id, "nueva", created_at=T0 + 20)

    assert [note.body for note in repository.list_notes(project_id)] == [
        "nueva",
        "media",
        "vieja",
    ]


def test_notes_with_the_same_time_come_in_reverse_creation_order(repository, project_id):
    add(repository, project_id, "primera")
    add(repository, project_id, "segunda")

    assert [note.body for note in repository.list_notes(project_id)] == ["segunda", "primera"]


def test_editing_a_note_keeps_its_creation_time(db_path, repository, project_id):
    note = add(repository, project_id, "texto viejo")
    note.edit("texto nuevo")

    repository.save_note(note)

    stored = SqliteProjectRepository(db_path).list_notes(project_id)[0]
    assert stored.body == "texto nuevo"
    assert stored.created_at == T0


def test_deleting_a_note_leaves_the_others(repository, project_id):
    keep = add(repository, project_id, "se queda", created_at=T0)
    gone = add(repository, project_id, "se va", created_at=T0 + 10)

    repository.delete_note(gone.id)

    assert [note.id for note in repository.list_notes(project_id)] == [keep.id]


def test_notes_belong_to_their_own_project(repository):
    first = repository.add(Project("primera"), T0)
    second = repository.add(Project("segunda"), T0)
    add(repository, first, "de la primera")
    add(repository, second, "de la segunda")

    assert [note.body for note in repository.list_notes(first)] == ["de la primera"]
    assert [note.body for note in repository.list_notes(second)] == ["de la segunda"]


def test_a_note_needs_an_existing_project(repository):
    with pytest.raises(sqlite3.IntegrityError):
        repository.add_note(9999, Note("huérfana", T0))
