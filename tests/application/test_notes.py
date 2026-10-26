"""Note use cases, including what happens when saving fails (RF-14, RF-15, T22)."""

import pytest

from crochet_tracker.application.create_project import create_project
from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.notes import add_note, delete_note, edit_note
from crochet_tracker.domain.errors import EmptyNoteText
from crochet_tracker.domain.undo import Undo
from tests.application.fakes import FakeClock, FakeRepository


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def undo() -> Undo:
    return Undo()


@pytest.fixture
def project(repository, clock):
    return create_project(repository, clock, "Bufanda")


def test_a_note_is_stored_with_its_date(repository, clock, project, undo):
    note = add_note(repository, clock, project, "  primera vuelta  ", undo)
    assert note.id is not None
    assert note.created_at == clock.now()
    stored = repository.list_notes(project.id)[0]
    assert (stored.body, stored.created_at) == ("  primera vuelta  ", clock.now())


def test_newest_note_comes_first(repository, clock, project, undo):
    add_note(repository, clock, project, "vieja", undo)
    clock.advance(60)
    add_note(repository, clock, project, "nueva", undo)
    assert [n.body for n in repository.list_notes(project.id)] == ["nueva", "vieja"]


@pytest.mark.parametrize("body", ["", "   ", "\n\t"])
def test_a_blank_note_is_rejected(repository, clock, project, undo, body):
    with pytest.raises(EmptyNoteText):
        add_note(repository, clock, project, body, undo)
    assert repository.list_notes(project.id) == []


def test_a_note_that_cannot_be_saved_is_not_stored(repository, clock, project, undo):
    repository.fail_on_write = True
    with pytest.raises(SaveFailed):
        add_note(repository, clock, project, "primera", undo)
    assert repository.list_notes(project.id) == []
    assert not undo.is_available(clock.now())


def test_editing_keeps_the_creation_date(repository, clock, project, undo):
    note = add_note(repository, clock, project, "primera", undo)
    created_at = note.created_at
    clock.advance(60)
    edit_note(repository, clock, note, "primera vuelta", undo)
    stored = repository.list_notes(project.id)[0]
    assert (stored.body, stored.created_at) == ("primera vuelta", created_at)


def test_editing_to_a_blank_text_keeps_the_previous_one(repository, clock, project, undo):
    note = add_note(repository, clock, project, "primera", undo)
    with pytest.raises(EmptyNoteText):
        edit_note(repository, clock, note, "   ", undo)
    assert note.body == "primera"
    assert repository.list_notes(project.id)[0].body == "primera"


def test_a_failed_edit_keeps_the_previous_text(repository, clock, project, undo):
    note = add_note(repository, clock, project, "primera", undo)
    repository.fail_on_write = True
    with pytest.raises(SaveFailed):
        edit_note(repository, clock, note, "otra cosa", undo)
    assert note.body == "primera"
    assert repository.list_notes(project.id)[0].body == "primera"


def test_deleting_removes_the_note(repository, clock, project, undo):
    note = add_note(repository, clock, project, "primera", undo)
    delete_note(repository, clock, project, note, undo)
    assert repository.list_notes(project.id) == []


def test_a_failed_delete_keeps_the_note(repository, clock, project, undo):
    note = add_note(repository, clock, project, "primera", undo)
    repository.fail_on_write = True
    with pytest.raises(SaveFailed):
        delete_note(repository, clock, project, note, undo)
    repository.fail_on_write = False
    assert [n.body for n in repository.list_notes(project.id)] == ["primera"]


def test_notes_belong_to_their_own_project(repository, clock, project, undo):
    other = create_project(repository, clock, "Gorro")
    add_note(repository, clock, project, "de la bufanda", undo)
    add_note(repository, clock, other, "del gorro", undo)
    assert [n.body for n in repository.list_notes(project.id)] == ["de la bufanda"]
    assert [n.body for n in repository.list_notes(other.id)] == ["del gorro"]
