"""Guide on screen: the saved page, its limits and unreadable files (RF-8, RF-9, RF-10, T34)."""

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from crochet_tracker.application.create_project import create_project
from crochet_tracker.presentation import guide_view, strings
from crochet_tracker.presentation.guide_view import GuideView


def build_pdf(pages: int, width: int = 200, height: int = 300) -> bytes:
    """A tiny but valid PDF with `pages` empty pages of that size in points."""
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(pages))
    parts = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {pages} >>",
    ]
    for index in range(pages):
        parts.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
            f"/Contents {4 + 2 * index} 0 R >>"
        )
        parts.append("<< /Length 0 >>\nstream\n\nendstream")

    body = "%PDF-1.4\n"
    offsets = []
    for number, part in enumerate(parts, start=1):
        offsets.append(len(body))
        body += f"{number} 0 obj\n{part}\nendobj\n"
    xref_at = len(body)
    body += f"xref\n0 {len(parts) + 1}\n0000000000 65535 f \n"
    body += "".join(f"{offset:010d} 00000 n \n" for offset in offsets)
    body += (
        f"trailer\n<< /Size {len(parts) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_at}\n%%EOF\n"
    )
    return body.encode("latin-1")


@pytest.fixture
def pdf(tmp_path):
    def write(pages: int = 3) -> str:
        target = tmp_path / f"guia-{pages}.pdf"
        target.write_bytes(build_pdf(pages))
        return str(target)

    return write


@pytest.fixture
def view(qtbot, repository, clock, guides) -> GuideView:
    widget = GuideView(repository, clock, guides)
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def warnings(monkeypatch) -> list[str]:
    shown: list[str] = []
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _parent, _title, text: shown.append(text)
    )
    return shown


def with_guide(repository, clock, guides, pdf, pages: int = 3, page: int = 1):
    project = create_project(repository, clock, "Bufanda")
    project.guide_file = guides.copy(project.id, __import__("pathlib").Path(pdf(pages)))
    project.guide_page = page
    repository.save(project, clock.now())
    return project


def test_without_a_guide_it_says_so_and_offers_one(view, repository, clock) -> None:
    view.set_project(create_project(repository, clock, "Bufanda"))

    assert view.notice_label.text() == strings.NO_GUIDE
    assert view.notice_label.isHidden() is False
    assert view.attach_button.isHidden() is False
    assert view.next_button.isHidden() is True


def test_a_project_never_opened_shows_the_first_page(view, repository, clock, guides, pdf) -> None:
    project = with_guide(repository, clock, guides, pdf)

    view.set_project(project)

    assert view.page_label.text() == strings.PAGE.format(page=1, total=3)
    assert view.image_label.pixmap().isNull() is False
    assert view.previous_button.isEnabled() is False
    assert view.next_button.isEnabled() is True


def test_it_opens_where_the_user_left(view, repository, clock, guides, pdf) -> None:
    project = with_guide(repository, clock, guides, pdf, page=2)

    view.set_project(project)

    assert view.page_label.text() == strings.PAGE.format(page=2, total=3)


def test_the_next_page_is_saved_at_once(view, repository, clock, guides, pdf) -> None:
    project = with_guide(repository, clock, guides, pdf)

    view.set_project(project)
    view.next_button.click()

    assert view.page_label.text() == strings.PAGE.format(page=2, total=3)
    assert repository.get(project.id).guide_page == 2


def test_the_previous_page_is_saved_at_once(view, repository, clock, guides, pdf) -> None:
    project = with_guide(repository, clock, guides, pdf, page=3)

    view.set_project(project)
    view.previous_button.click()

    assert view.page_label.text() == strings.PAGE.format(page=2, total=3)
    assert repository.get(project.id).guide_page == 2


def test_the_last_page_cannot_go_further(view, repository, clock, guides, pdf) -> None:
    project = with_guide(repository, clock, guides, pdf, pages=2, page=2)

    view.set_project(project)

    assert view.next_button.isEnabled() is False
    assert view.previous_button.isEnabled() is True


def test_a_saved_page_past_the_end_is_pulled_back(
    view, repository, clock, guides, pdf
) -> None:
    project = with_guide(repository, clock, guides, pdf, pages=2, page=9)

    view.set_project(project)

    assert view.page_label.text() == strings.PAGE.format(page=2, total=2)


def test_a_page_that_cannot_be_drawn_only_spoils_itself(
    view, repository, clock, guides, pdf, monkeypatch
) -> None:
    def explode(document, index):
        if index == 1:
            raise RuntimeError("página dañada")
        return guide_view.QPixmap(4, 4)

    monkeypatch.setattr(guide_view, "render_page", explode)
    project = with_guide(repository, clock, guides, pdf)

    view.set_project(project)
    view.next_button.click()

    assert view.image_label.text() == strings.PAGE_FAILED
    assert view.next_button.isEnabled() is True
    view.next_button.click()
    assert view.page_label.text() == strings.PAGE.format(page=3, total=3)
    assert view.image_label.text() == ""


def test_broken_stored_file_behaves_as_no_guide(
    view, repository, clock, guides, pdf
) -> None:
    project = with_guide(repository, clock, guides, pdf)
    stored = guides.path(project.guide_file)
    stored.write_bytes(b"esto no es un PDF")

    view.set_project(project)

    assert view.notice_label.text() == strings.GUIDE_UNREADABLE
    assert view.attach_button.isHidden() is False
    assert project.guide_file is None


def test_a_missing_stored_file_behaves_as_no_guide(
    view, repository, clock, guides, pdf
) -> None:
    project = with_guide(repository, clock, guides, pdf)
    guides.path(project.guide_file).unlink()

    view.set_project(project)

    assert view.notice_label.text() == strings.GUIDE_MISSING
    assert view.attach_button.isHidden() is False
    assert project.guide_file is None


def test_attaching_a_pdf_shows_it_without_restarting(
    view, repository, clock, guides, pdf, monkeypatch
) -> None:
    project = create_project(repository, clock, "Bufanda")
    view.set_project(project)
    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", lambda *_args: (pdf(2), strings.PDF_FILTER)
    )

    view.attach_button.click()

    assert project.guide_file is not None
    assert view.page_label.text() == strings.PAGE.format(page=1, total=2)
    assert repository.get(project.id).guide_file == project.guide_file


def test_cancelling_the_file_dialog_changes_nothing(
    view, repository, clock, guides, pdf, monkeypatch
) -> None:
    project = create_project(repository, clock, "Bufanda")
    view.set_project(project)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args: ("", ""))

    view.attach_button.click()

    assert project.guide_file is None
    assert view.notice_label.text() == strings.NO_GUIDE


def test_a_file_that_is_not_a_pdf_warns_and_stays_without_guide(
    qtbot, repository, clock, warnings, monkeypatch, tmp_path
) -> None:
    from crochet_tracker.infrastructure.guide_store import GuideStore

    not_a_pdf = tmp_path / "notas.txt"
    not_a_pdf.write_text("hola", encoding="utf-8")
    view = GuideView(repository, clock, GuideStore(tmp_path))
    qtbot.addWidget(view)
    project = create_project(repository, clock, "Bufanda")
    view.set_project(project)
    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", lambda *_args: (str(not_a_pdf), strings.PDF_FILTER)
    )

    view.attach_button.click()

    assert warnings == [strings.GUIDE_UNREADABLE]
    assert project.guide_file is None


def test_a_project_with_a_guide_does_not_offer_another(
    view, repository, clock, guides, pdf
) -> None:
    view.set_project(with_guide(repository, clock, guides, pdf))

    assert view.attach_button.isHidden() is True


def test_a_page_keeps_its_size_inside_the_scroll_area(
    view, repository, clock, guides, pdf
) -> None:
    view.resize(200, 200)

    view.set_project(with_guide(repository, clock, guides, pdf))

    assert view.image_label.size() == view.image_label.pixmap().size()


def test_a_page_taller_than_the_view_scrolls_with_the_bar_and_the_wheel(
    view, repository, clock, guides, pdf
) -> None:
    view.resize(200, 200)
    view.set_project(with_guide(repository, clock, guides, pdf))
    _show(view)
    bar = view.scroll.verticalScrollBar()

    assert bar.maximum() > 0
    assert bar.value() == 0

    QApplication.sendEvent(view.scroll.viewport(), _one_wheel_step_down())

    assert bar.value() > 0


def test_a_new_page_starts_at_the_top(view, repository, clock, guides, pdf) -> None:
    view.resize(200, 200)
    view.set_project(with_guide(repository, clock, guides, pdf))
    _show(view)
    bar = view.scroll.verticalScrollBar()
    bar.setValue(bar.maximum())

    view.next_button.click()

    assert bar.value() == 0


def _show(view) -> None:
    """Scroll bars only get their range once the widget is on screen."""
    view.show()
    QApplication.processEvents()


def _one_wheel_step_down() -> QWheelEvent:
    return QWheelEvent(
        QPointF(10, 10),
        QPointF(10, 10),
        QPoint(),
        QPoint(0, -120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )

