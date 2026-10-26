"""Notes panel: add, edit with Save/Cancel and delete with confirmation (RF-14, RF-15, T29)."""

import re

import pytest
from PySide6.QtWidgets import QMessageBox

from crochet_tracker.application.create_project import create_project
from crochet_tracker.presentation import notes_panel, strings


@pytest.fixture
def project(repository, clock):
    return create_project(repository, clock, "Bufanda")


@pytest.fixture
def panel(window, project):
    window.open_project(project)
    return window.project_view.notes_panel


@pytest.fixture
def warnings(monkeypatch) -> list[str]:
    shown: list[str] = []
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _parent, _title, text: shown.append(text)
    )
    return shown


@pytest.fixture
def delete_accepted(monkeypatch) -> None:
    monkeypatch.setattr(notes_panel, "confirm_delete_note", lambda _parent: True)


@pytest.fixture
def delete_cancelled(monkeypatch) -> None:
    monkeypatch.setattr(notes_panel, "confirm_delete_note", lambda _parent: False)


def add(panel, text: str) -> None:
    panel.new_text.setPlainText(text)
    panel.add_button.click()


def test_a_new_note_appears_with_its_date(panel) -> None:
    add(panel, "Se acabó la lana gris")

    assert panel.notes_list.count() == 1
    row = panel.notes_list.item(0).text()
    assert row.endswith("Se acabó la lana gris")
    assert re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", row)


def test_the_newest_note_goes_first(panel, clock) -> None:
    add(panel, "Primera")
    clock.advance(60)
    add(panel, "Segunda")

    assert panel.notes_list.item(0).text().endswith("Segunda")
    assert panel.notes_list.item(1).text().endswith("Primera")


def test_adding_clears_the_draft(panel) -> None:
    add(panel, "Primera")

    assert panel.new_text.toPlainText() == ""


@pytest.mark.parametrize("blank", ["", "   ", "\n\t "])
def test_a_blank_note_warns_and_is_not_stored(panel, warnings, blank) -> None:
    add(panel, blank)

    assert warnings == [strings.NOTE_REQUIRED]
    assert panel.notes_list.count() == 0


def test_editing_keeps_the_creation_date(panel, repository, project, clock) -> None:
    add(panel, "Primera")
    created_at = repository.list_notes(project.id)[0].created_at
    clock.advance(600)
    panel.notes_list.setCurrentRow(0)

    panel.edit_text.setPlainText("Primera, corregida")
    panel.save_button.click()

    stored = repository.list_notes(project.id)[0]
    assert stored.body == "Primera, corregida"
    assert stored.created_at == created_at


def test_cancelling_restores_the_previous_text(panel, repository, project) -> None:
    add(panel, "Primera")
    panel.notes_list.setCurrentRow(0)
    panel.edit_text.setPlainText("A medias")

    panel.cancel_button.click()

    assert panel.edit_text.toPlainText() == "Primera"
    assert repository.list_notes(project.id)[0].body == "Primera"


def test_a_blank_edit_warns_and_keeps_the_text(panel, repository, project, warnings) -> None:
    add(panel, "Primera")
    panel.notes_list.setCurrentRow(0)

    panel.edit_text.setPlainText("   ")
    panel.save_button.click()

    assert warnings == [strings.NOTE_REQUIRED]
    assert panel.edit_text.toPlainText() == "Primera"
    assert repository.list_notes(project.id)[0].body == "Primera"


def test_editing_without_a_selection_writes_nothing(panel, repository, project) -> None:
    add(panel, "Primera")

    panel.save_button.click()

    assert repository.list_notes(project.id)[0].body == "Primera"


def test_deleting_asks_and_removes_the_note(
    panel, repository, project, delete_accepted
) -> None:
    add(panel, "Primera")
    panel.notes_list.setCurrentRow(0)

    panel.delete_button.click()

    assert panel.notes_list.count() == 0
    assert repository.list_notes(project.id) == []


def test_cancelling_the_delete_keeps_the_note(
    panel, repository, project, delete_cancelled
) -> None:
    add(panel, "Primera")
    panel.notes_list.setCurrentRow(0)

    panel.delete_button.click()

    assert panel.notes_list.count() == 1
    assert len(repository.list_notes(project.id)) == 1


def test_notes_are_still_there_when_the_project_is_reopened(
    window, panel, repository, project
) -> None:
    add(panel, "Primera")

    window.open_project(repository.get(project.id))

    assert window.project_view.notes_panel.notes_list.count() == 1


def test_the_editor_is_disabled_without_a_selection(panel) -> None:
    add(panel, "Primera")

    panel.notes_list.setCurrentRow(0)
    assert panel.save_button.isEnabled() is True

    panel.notes_list.clearSelection()
    panel.notes_list.setCurrentRow(-1)
    assert panel.save_button.isEnabled() is False
