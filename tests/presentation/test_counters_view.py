"""Counters on screen: +1/-1, floor at zero and a failed save (RF-11..RF-13, T28)."""

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


def test_a_new_project_starts_at_zero(view) -> None:
    assert view.rows_label.text() == "0"
    assert view.knots_label.text() == "0"


def test_adding_a_row_counts_and_saves(view, repository, project) -> None:
    view.rows_up.click()

    assert view.rows_label.text() == "1"
    assert repository.get(project.id).rows_done == 1


def test_adding_a_knot_counts_and_saves(view, repository, project) -> None:
    view.knots_up.click()

    assert view.knots_label.text() == "1"
    assert repository.get(project.id).knots_done == 1


def test_the_two_counters_are_independent(view) -> None:
    view.rows_up.click()
    view.knots_up.click()
    view.knots_up.click()

    assert view.rows_label.text() == "1"
    assert view.knots_label.text() == "2"


def test_decreasing_is_disabled_at_zero(view) -> None:
    assert view.rows_down.isEnabled() is False
    assert view.knots_down.isEnabled() is False


def test_decreasing_works_above_zero(view, repository, project) -> None:
    view.rows_up.click()
    view.rows_up.click()

    view.rows_down.click()

    assert view.rows_label.text() == "1"
    assert repository.get(project.id).rows_done == 1


def test_decreasing_back_to_zero_disables_the_button(view) -> None:
    view.rows_up.click()
    view.rows_down.click()

    assert view.rows_label.text() == "0"
    assert view.rows_down.isEnabled() is False


def test_big_counters_are_shown_in_full(view, project) -> None:
    project.restore_rows(100_001)

    view.refresh()

    assert view.rows_label.text() == "100001"


def test_a_failed_save_warns_and_keeps_the_previous_value(
    view, repository, project, warnings
) -> None:
    repository.fail_on_write = True

    view.rows_up.click()

    assert warnings == [strings.SAVE_FAILED]
    assert view.rows_label.text() == "0"
    assert repository.get(project.id).rows_done == 0


def test_reopening_shows_the_saved_values(window, view, repository, project) -> None:
    view.rows_up.click()
    view.knots_up.click()

    window.open_project(repository.get(project.id))

    assert window.project_view.rows_label.text() == "1"
    assert window.project_view.knots_label.text() == "1"
