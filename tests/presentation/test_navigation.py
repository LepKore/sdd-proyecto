"""Window opens on the list, one project at a time, back returns (RF-2, RF-3, T25)."""

from PySide6.QtWidgets import QLabel, QPushButton

from crochet_tracker.application.create_project import create_project
from crochet_tracker.presentation import strings


def test_window_opens_on_the_list(window) -> None:
    assert window.stack.currentWidget() is window.list_view


def test_opening_a_project_shows_its_name(window, repository, clock) -> None:
    project = create_project(repository, clock, "Bufanda de lana")

    window.open_project(project)

    assert window.stack.currentWidget() is window.project_view
    assert window.project_view.name_edit.text() == "Bufanda de lana"


def test_only_one_project_is_open_at_a_time(window, repository, clock) -> None:
    window.open_project(create_project(repository, clock, "Bufanda"))

    window.open_project(create_project(repository, clock, "Amigurumi"))

    assert window.project_view.name_edit.text() == "Amigurumi"


def test_back_button_returns_to_the_list(window, repository, clock) -> None:
    window.open_project(create_project(repository, clock, "Bufanda"))

    window.project_view.back_button.click()

    assert window.stack.currentWidget() is window.list_view


def test_back_keeps_the_project_in_the_list(window, repository, clock) -> None:
    window.open_project(create_project(repository, clock, "Bufanda"))

    window.project_view.back_button.click()

    assert window.list_view.list_widget.count() == 1


def test_every_visible_text_is_spanish(window) -> None:
    declared = {
        value
        for name, value in vars(strings).items()
        if name.isupper() and isinstance(value, str)
    }
    labels = [label.text() for label in window.findChildren(QLabel)]
    buttons = [button.text() for button in window.findChildren(QPushButton)]

    for text in labels + buttons:
        assert text == "" or text in declared, f"texto no declarado en strings.py: {text!r}"
