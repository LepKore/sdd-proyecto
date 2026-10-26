"""Finished projects keep their row; deleting asks first (RF-2, RF-6, T27)."""

import pytest

from crochet_tracker.application.create_project import create_project
from crochet_tracker.application.open_project import open_project
from crochet_tracker.application.set_finished import set_finished
from crochet_tracker.domain.note import Note
from crochet_tracker.presentation import project_list_view


@pytest.fixture
def confirmations(monkeypatch) -> list[str]:
    """Records the names the confirmation asks about; the dialog itself is [manual]."""
    asked: list[str] = []
    monkeypatch.setattr(
        project_list_view,
        "confirm_delete",
        lambda _parent, name: asked.append(name) or False,
    )
    return asked


@pytest.fixture
def accepted(monkeypatch) -> None:
    monkeypatch.setattr(project_list_view, "confirm_delete", lambda _parent, _name: True)


@pytest.fixture
def finished_project(repository, clock):
    project = create_project(repository, clock, "Amigurumi pulpo")
    set_finished(repository, clock, project)
    return project


def test_a_finished_project_is_labelled_and_stays_in_the_list(
    window, repository, finished_project
) -> None:
    window.list_view.refresh()

    assert window.list_view.list_widget.count() == 1
    row = window.list_view.list_widget.item(0).text()
    assert row.startswith("Amigurumi pulpo")
    assert "Terminado" in row


def test_a_finished_project_can_still_be_opened(window, finished_project) -> None:
    window.list_view.refresh()
    window.list_view.list_widget.setCurrentRow(0)

    window.list_view.open_selected()

    assert window.stack.currentWidget() is window.project_view


def test_deleting_asks_with_the_project_name(
    window, finished_project, confirmations
) -> None:
    window.list_view.refresh()
    window.list_view.list_widget.setCurrentRow(0)

    window.list_view.delete()

    assert confirmations == ["Amigurumi pulpo"]


def test_refresh_selects_the_first_project_for_actions(
    window, repository, clock, confirmations
) -> None:
    create_project(repository, clock, "Bufanda")
    window.list_view.refresh()

    assert window.list_view.list_widget.currentRow() == 0
    assert window.list_view.delete_button.isEnabled()


def test_cancelling_keeps_the_project(window, repository, clock, confirmations) -> None:
    create_project(repository, clock, "Bufanda")
    window.list_view.refresh()
    window.list_view.list_widget.setCurrentRow(0)

    window.list_view.delete()

    assert len(repository.projects) == 1
    assert window.list_view.list_widget.count() == 1


def test_confirming_removes_it_from_the_list(
    window, repository, clock, accepted
) -> None:
    create_project(repository, clock, "Bufanda")
    window.list_view.refresh()
    window.list_view.list_widget.setCurrentRow(0)

    window.list_view.delete()

    assert repository.projects == {}
    assert window.list_view.list_widget.count() == 0
    assert window.list_view.empty_label.isHidden() is False


def test_confirming_removes_its_notes(window, repository, clock, accepted) -> None:
    project = create_project(repository, clock, "Bufanda")
    repository.add_note(project.id, Note(body="Se acabó la lana", created_at=clock.now()))
    window.list_view.refresh()
    window.list_view.list_widget.setCurrentRow(0)

    window.list_view.delete()

    assert repository.notes == {}


def test_the_open_project_is_what_can_be_deleted(
    window, repository, clock, confirmations
) -> None:
    create_project(repository, clock, "Bufanda")
    create_project(repository, clock, "Amigurumi")
    window.list_view.refresh()
    window.list_view.list_widget.setCurrentRow(1)

    window.list_view.delete()

    assert confirmations == ["Bufanda"]


def test_opening_from_the_list_does_not_reorder_it(window, repository, clock) -> None:
    first = create_project(repository, clock, "Bufanda")
    clock.advance(60)
    create_project(repository, clock, "Amigurumi")
    window.list_view.refresh()

    window.open_project(open_project(repository, first.id))
    window.show_list()

    rows = [window.list_view.list_widget.item(i).text() for i in range(2)]
    assert rows[0].startswith("Amigurumi")
