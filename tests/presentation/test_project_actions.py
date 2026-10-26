"""Renaming and marking finished from the project screen (RF-4, RF-5, T31)."""

import pytest
from PySide6.QtWidgets import QMessageBox

from crochet_tracker.application.create_project import create_project
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


def rename(view, name: str) -> None:
    view.name_edit.setText(name)
    view.rename_button.click()


def test_the_screen_shows_the_saved_name(view) -> None:
    assert view.name_edit.text() == "Bufanda"


def test_renaming_shows_the_new_name_on_the_screen(view) -> None:
    rename(view, "Bufanda de lana")

    assert view.name_edit.text() == "Bufanda de lana"


def test_renaming_is_saved(view, repository, project) -> None:
    rename(view, "Bufanda de lana")

    assert repository.get(project.id).name == "Bufanda de lana"


def test_renaming_shows_the_new_name_in_the_list(window, view) -> None:
    rename(view, "Bufanda de lana")

    view.back_button.click()

    row = window.list_view.list_widget.item(0).text()
    assert row.startswith("Bufanda de lana")


def test_renaming_trims_the_ends(view) -> None:
    rename(view, "  Bufanda de lana  ")

    assert view.name_edit.text() == "Bufanda de lana"


@pytest.mark.parametrize("blank", ["", "   ", "\n\t "])
def test_a_blank_name_warns_and_keeps_the_previous_one(
    view, repository, project, warnings, blank
) -> None:
    rename(view, blank)

    assert warnings == [strings.NAME_REQUIRED]
    assert view.name_edit.text() == "Bufanda"
    assert repository.get(project.id).name == "Bufanda"


def test_a_failed_rename_warns_and_keeps_the_previous_name(
    view, repository, project, warnings
) -> None:
    repository.fail_on_write = True

    rename(view, "Bufanda de lana")

    assert warnings == [strings.SAVE_FAILED]
    assert view.name_edit.text() == "Bufanda"
    assert repository.get(project.id).name == "Bufanda"


def test_marking_finished_shows_the_label(view) -> None:
    view.finished_button.click()

    assert view.finished_label.isHidden() is False
    assert view.finished_button.text() == strings.MARK_UNFINISHED


def test_marking_finished_is_saved(view, repository, project) -> None:
    view.finished_button.click()

    assert repository.get(project.id).is_finished is True


def test_unmarking_hides_the_label(view) -> None:
    view.finished_button.click()

    view.finished_button.click()

    assert view.finished_label.isHidden() is True
    assert view.finished_button.text() == strings.MARK_FINISHED
    assert view._project.is_finished is False


def test_a_finished_project_still_counts(view, repository, project) -> None:
    view.finished_button.click()

    view.rows_up.click()

    assert view.rows_label.text() == "1"
    assert repository.get(project.id).is_finished is True


def test_a_failed_toggle_warns_and_keeps_the_state(
    view, repository, project, warnings
) -> None:
    repository.fail_on_write = True

    view.finished_button.click()

    assert warnings == [strings.SAVE_FAILED]
    assert view.finished_label.isHidden() is True
    assert repository.get(project.id).is_finished is False
