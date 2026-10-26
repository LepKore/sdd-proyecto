"""The undo banner appears, expires and goes away by itself (RF-16, T30)."""

import pytest
from PySide6.QtWidgets import QMessageBox

from crochet_tracker.application.create_project import create_project
from crochet_tracker.domain.undo import UNDO_WINDOW_SECONDS
from crochet_tracker.presentation import strings


@pytest.fixture
def project(repository, clock):
    return create_project(repository, clock, "Bufanda")


@pytest.fixture
def view(window, project):
    window.open_project(project)
    return window.project_view


@pytest.fixture
def warnings(monkeypatch) -> list[str]:
    shown: list[str] = []
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _parent, _title, text: shown.append(text)
    )
    return shown


def test_no_banner_without_a_change(view) -> None:
    assert view.undo_button.isHidden() is True
    assert view.undo_label.isHidden() is True


def test_counting_offers_to_undo(view) -> None:
    view.rows_up.click()

    assert view.undo_button.isHidden() is False


def test_undoing_a_counter_restores_the_previous_value(view) -> None:
    view.rows_up.click()
    view.rows_up.click()

    view.undo_button.click()

    assert view.rows_label.text() == "1"


def test_the_banner_disappears_after_undoing(view) -> None:
    view.rows_up.click()

    view.undo_button.click()

    assert view.undo_button.isHidden() is True


def test_the_banner_expires_after_ten_minutes(view, clock) -> None:
    view.rows_up.click()
    clock.advance(UNDO_WINDOW_SECONDS + 1)

    view._refresh_undo()

    assert view.undo_button.isHidden() is True


def test_the_banner_lasts_until_the_last_second(view, clock) -> None:
    view.rows_up.click()
    clock.advance(UNDO_WINDOW_SECONDS)

    view._refresh_undo()

    assert view.undo_button.isHidden() is False


def test_renaming_does_not_offer_undo(view) -> None:
    view.name_edit.setText("Bufanda de lana")

    view.rename_button.click()

    assert view.undo_button.isHidden() is True


def test_marking_finished_does_not_offer_undo(view) -> None:
    view.finished_button.click()

    assert view.undo_button.isHidden() is True


def test_renaming_keeps_the_pending_undo(view) -> None:
    view.rows_up.click()

    view.name_edit.setText("Bufanda de lana")
    view.rename_button.click()

    assert view.undo_button.isHidden() is False


def test_marking_finished_keeps_the_pending_undo(view) -> None:
    view.rows_up.click()

    view.finished_button.click()

    assert view.undo_button.isHidden() is False


def test_a_failed_save_offers_nothing_to_undo(view, repository, warnings) -> None:
    repository.fail_on_write = True

    view.rows_up.click()

    assert warnings == [strings.SAVE_FAILED]
    assert view.undo_button.isHidden() is True


def test_adding_a_note_offers_undo(view) -> None:
    view.notes_panel.new_text.setPlainText("Se acabó la lana")

    view.notes_panel.add_button.click()

    assert view.undo_button.isHidden() is False


def test_undoing_a_new_note_removes_it(view, repository, project) -> None:
    view.notes_panel.new_text.setPlainText("Se acabó la lana")
    view.notes_panel.add_button.click()

    view.undo_button.click()

    assert repository.list_notes(project.id) == []
    assert view.notes_panel.notes_list.count() == 0


def test_going_back_to_the_list_discards_the_undo(window, view, repository, project) -> None:
    view.rows_up.click()

    view.back_button.click()
    window.open_project(repository.get(project.id))

    assert window.project_view.undo_button.isHidden() is True


def test_opening_another_project_discards_the_undo(view, repository, clock) -> None:
    view.rows_up.click()

    other = create_project(repository, clock, "Amigurumi")
    view.set_project(other)

    assert view.undo_button.isHidden() is True
