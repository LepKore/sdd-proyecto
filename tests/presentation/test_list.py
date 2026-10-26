"""The list: empty state, newest first and creating projects (RF-1, RF-2, T26)."""

import re

import pytest
from PySide6.QtWidgets import QMessageBox

from crochet_tracker.application.create_project import create_project
from crochet_tracker.presentation import project_list_view, strings


@pytest.fixture
def asked(monkeypatch):
    """Stand-in for the name dialog, which is [manual]; returns the given answer."""

    def set_answer(name: str, accepted: bool = True) -> None:
        monkeypatch.setattr(
            project_list_view, "ask_project_name", lambda _parent: (name, accepted)
        )

    return set_answer


@pytest.fixture
def warnings(monkeypatch) -> list[str]:
    shown: list[str] = []
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _parent, _title, text: shown.append(text)
    )
    return shown


def test_empty_state_is_shown_without_projects(window) -> None:
    assert window.list_view.empty_label.isHidden() is False
    assert window.list_view.list_widget.isHidden() is True


def test_empty_state_hides_when_a_project_exists(window, repository, clock) -> None:
    create_project(repository, clock, "Bufanda")

    window.list_view.refresh()

    assert window.list_view.empty_label.isHidden() is True
    assert window.list_view.list_widget.count() == 1


def test_projects_are_listed_newest_change_first(window, repository, clock) -> None:
    create_project(repository, clock, "Bufanda")
    clock.advance(60)
    create_project(repository, clock, "Amigurumi")

    window.list_view.refresh()

    rows = [window.list_view.list_widget.item(i).text() for i in range(2)]
    assert rows[0].startswith("Amigurumi")
    assert rows[1].startswith("Bufanda")


def test_a_row_shows_when_it_changed_last(window, repository, clock) -> None:
    create_project(repository, clock, "Bufanda")

    window.list_view.refresh()

    row = window.list_view.list_widget.item(0).text()
    assert re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", row)


def test_a_long_name_is_elided_and_kept_in_the_tooltip(window, repository, clock) -> None:
    name = "x" * 100
    create_project(repository, clock, name)

    window.list_view.refresh()

    assert window.list_view.list_widget.item(0).toolTip() == name


def test_creating_a_project_opens_it(window, repository, clock, asked) -> None:
    asked("Bufanda de lana")

    window.list_view.new_button.click()

    assert window.stack.currentWidget() is window.project_view
    assert window.project_view.name_edit.text() == "Bufanda de lana"
    assert len(repository.projects) == 1


@pytest.mark.parametrize("blank", ["", "   ", "\n\t "])
def test_creating_without_a_name_warns_and_creates_nothing(
    window, repository, asked, warnings, blank
) -> None:
    asked(blank)

    window.list_view.new_button.click()

    assert warnings == [strings.NAME_REQUIRED]
    assert repository.projects == {}
    assert window.stack.currentWidget() is window.list_view


def test_cancelling_creates_nothing(window, repository, asked) -> None:
    asked("Bufanda", accepted=False)

    window.list_view.new_button.click()

    assert repository.projects == {}
    assert window.list_view.list_widget.count() == 0


def test_a_repeated_name_is_accepted(window, repository, clock, asked) -> None:
    asked("Bufanda")

    window.list_view.new_button.click()
    window.show_list()
    window.list_view.new_button.click()

    assert len(repository.projects) == 2
