"""Layout of the project screen: notes on the right and a window the page cannot grow (T34)."""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from crochet_tracker.application.create_project import create_project
from tests.presentation.test_guide_view import build_pdf


def _huge_page(tmp_path: Path) -> Path:
    """A page far bigger than any screen once it is rendered at RENDER_SCALE."""
    target = tmp_path / "grande.pdf"
    target.write_bytes(build_pdf(1, width=2000, height=3000))
    return target


def test_the_notes_sit_to_the_right_of_the_guide(window, repository, clock) -> None:
    window.show()
    window.open_project(create_project(repository, clock, "Bufanda"))
    QApplication.processEvents()

    guide = window.project_view.guide_view.geometry()
    notes = window.project_view.notes_panel.geometry()

    assert notes.left() >= guide.right()


def test_a_huge_page_does_not_resize_the_window(
    window, repository, clock, guides, tmp_path
) -> None:
    window.show()
    window.open_project(create_project(repository, clock, "Sin guía"))
    QApplication.processEvents()
    without_guide = window.size()

    project = create_project(repository, clock, "Con guía")
    project.guide_file = guides.copy(project.id, _huge_page(tmp_path))
    repository.save(project, clock.now())
    window.open_project(repository.get(project.id))
    QApplication.processEvents()

    assert window.size() == without_guide


def test_the_window_never_starts_bigger_than_the_screen(window) -> None:
    visible = QApplication.primaryScreen().availableGeometry()

    assert window.width() <= visible.width()
    assert window.height() <= visible.height()
