"""Undo the last counter or note change (RF-16, T23)."""

import pytest

from crochet_tracker.application.counters import add_rows
from crochet_tracker.application.create_project import create_project
from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.notes import add_note, delete_note, edit_note
from crochet_tracker.application.open_project import open_project
from crochet_tracker.application.rename_project import rename_project
from crochet_tracker.application.set_finished import set_finished
from crochet_tracker.application.undo_last_change import can_undo, undo_last_change
from crochet_tracker.domain.undo import UNDO_WINDOW_SECONDS, Undo
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


def test_a_counter_goes_back_to_its_previous_value(repository, clock, project, undo):
    add_rows(repository, clock, project, undo)
    add_rows(repository, clock, project, undo)
    assert undo_last_change(clock, undo) is True
    assert project.rows_done == 1
    assert open_project(repository, project.id).rows_done == 1


def test_nothing_to_undo_reports_false(repository, clock, project, undo):
    assert can_undo(undo, clock) is False
    assert undo_last_change(clock, undo) is False


def test_only_one_step_is_offered(repository, clock, project, undo):
    add_rows(repository, clock, project, undo)
    add_rows(repository, clock, project, undo)
    undo_last_change(clock, undo)
    assert can_undo(undo, clock) is False
    assert undo_last_change(clock, undo) is False
    assert project.rows_done == 1


def test_undo_is_gone_after_the_window(repository, clock, project, undo):
    add_rows(repository, clock, project, undo)
    clock.advance(UNDO_WINDOW_SECONDS + 1)
    assert can_undo(undo, clock) is False
    assert undo_last_change(clock, undo) is False
    assert project.rows_done == 1


def test_undo_is_still_offered_at_the_last_second(repository, clock, project, undo):
    add_rows(repository, clock, project, undo)
    clock.advance(UNDO_WINDOW_SECONDS)
    assert can_undo(undo, clock) is True


def test_undoing_a_new_note_removes_it(repository, clock, project, undo):
    add_note(repository, clock, project, "primera", undo)
    undo_last_change(clock, undo)
    assert repository.list_notes(project.id) == []


def test_undoing_an_edit_brings_the_previous_text_back(repository, clock, project, undo):
    note = add_note(repository, clock, project, "primera", undo)
    edit_note(repository, clock, note, "otra cosa", undo)
    undo_last_change(clock, undo)
    assert note.body == "primera"
    assert repository.list_notes(project.id)[0].body == "primera"


def test_undoing_a_delete_brings_the_note_back_with_its_date(repository, clock, project, undo):
    note = add_note(repository, clock, project, "primera", undo)
    created_at = note.created_at
    clock.advance(60)
    delete_note(repository, clock, project, note, undo)
    undo_last_change(clock, undo)
    restored = repository.list_notes(project.id)[0]
    assert (restored.body, restored.created_at) == ("primera", created_at)


def test_changes_that_are_not_undoable_keep_the_pending_one(repository, clock, project, undo):
    add_rows(repository, clock, project, undo)
    rename_project(repository, clock, project, "Chal")
    set_finished(repository, clock, project)
    assert can_undo(undo, clock) is True
    assert undo_last_change(clock, undo) is True
    assert project.rows_done == 0


def test_a_failed_save_is_not_offered_for_undo(repository, clock, project, undo):
    repository.fail_on_write = True
    with pytest.raises(SaveFailed):
        add_rows(repository, clock, project, undo)
    assert can_undo(undo, clock) is False


def test_a_failed_undo_keeps_the_counter_where_it_was(repository, clock, project, undo):
    add_rows(repository, clock, project, undo)
    repository.fail_on_write = True
    with pytest.raises(SaveFailed):
        undo_last_change(clock, undo)
    assert project.rows_done == 1
    repository.fail_on_write = False
    assert open_project(repository, project.id).rows_done == 1


def test_leaving_the_project_discards_the_pending_undo(repository, clock, project, undo):
    add_rows(repository, clock, project, undo)
    undo.discard()
    assert can_undo(undo, clock) is False
