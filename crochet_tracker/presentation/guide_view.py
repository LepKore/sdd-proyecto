"""Guide on screen: render the stored PDF and move through its pages (RF-8, RF-9, RF-10).

This is the only place that turns a page into a picture; the page number is saved the
moment the user moves (RF-10), and a page that cannot be drawn only spoils itself (CL-14).
"""

from pathlib import Path

import pypdfium2 as pdfium
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from crochet_tracker.application.attach_guide import attach_guide
from crochet_tracker.application.change_page import change_page
from crochet_tracker.application.errors import GuideError, SaveFailed
from crochet_tracker.application.ports import Clock, GuideStore, ProjectRepository
from crochet_tracker.domain.project import Project
from crochet_tracker.presentation import strings

RENDER_SCALE = 2
FAILED_SIZE = 320


def render_page(document: pdfium.PdfDocument, index: int) -> QPixmap:
    """Paint one page as BGR pixels, so neither Pillow nor numpy is needed."""
    bitmap = document[index].render(scale=RENDER_SCALE)
    image = QImage(
        bytes(bitmap.buffer),
        bitmap.width,
        bitmap.height,
        bitmap.stride,
        QImage.Format.Format_BGR888,
    )
    return QPixmap.fromImage(image.copy())


class GuideView(QWidget):
    """Shows the guide of the open project, or how to get one."""

    def __init__(
        self,
        repository: ProjectRepository,
        clock: Clock,
        guides: GuideStore,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repository = repository
        self._clock = clock
        self._guides = guides
        self._project: Project | None = None
        self._document: pdfium.PdfDocument | None = None
        self._total = 0

        self.notice_label = QLabel()
        self.attach_button = QPushButton(strings.ATTACH_GUIDE)
        self.previous_button = QPushButton(strings.PREVIOUS_PAGE)
        self.next_button = QPushButton(strings.NEXT_PAGE)
        self.page_label = QLabel()
        self.image_label = QLabel()
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.image_label)
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        controls = QHBoxLayout()
        controls.addWidget(self.previous_button)
        controls.addStretch(1)
        controls.addWidget(self.page_label)
        controls.addStretch(1)
        controls.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.attach_button)
        layout.addWidget(self.notice_label)
        layout.addLayout(controls)
        layout.addWidget(self.scroll, 1)

        self.attach_button.clicked.connect(lambda: self.attach())
        self.previous_button.clicked.connect(lambda: self.move(-1))
        self.next_button.clicked.connect(lambda: self.move(1))

    def set_project(self, project: Project | None) -> None:
        """Open the guide of this project, or the empty state when it has none."""
        self._close()
        self._project = project
        if project is not None:
            self._open(project)
        self._refresh()

    def move(self, delta: int) -> None:
        """Go one page forward or back and save the page at once (RF-10)."""
        if self._project is None or self._document is None:
            return
        try:
            change_page(self._repository, self._clock, self._project, delta, self._total)
        except SaveFailed:
            QMessageBox.warning(self, strings.APP_TITLE, strings.SAVE_FAILED)
        self._refresh()

    def attach(self) -> None:
        """Copy the chosen PDF into the project and show it without restarting (RF-8)."""
        if self._project is None:
            return
        chosen, _filter = QFileDialog.getOpenFileName(
            self, strings.CHOOSE_GUIDE, "", strings.PDF_FILTER
        )
        if not chosen:
            return
        try:
            attach_guide(self._repository, self._clock, self._project, self._guides, Path(chosen))
        except GuideError:
            QMessageBox.warning(self, strings.ATTACH_GUIDE, strings.GUIDE_UNREADABLE)
            return
        except SaveFailed:
            QMessageBox.warning(self, strings.APP_TITLE, strings.SAVE_FAILED)
            return
        self.set_project(self._project)

    def _open(self, project: Project) -> None:
        if not project.guide_file:
            self.notice_label.setText(strings.NO_GUIDE)
            return
        stored = self._guides.path(project.guide_file)
        if stored is None:
            self.notice_label.setText(strings.GUIDE_MISSING)
            self._forget_guide(project)
            return
        try:
            self._document = pdfium.PdfDocument(str(stored))
        except pdfium.PdfiumError:
            self.notice_label.setText(strings.GUIDE_UNREADABLE)
            self._forget_guide(project)
            return
        self._total = len(self._document)
        project.guide_page = min(project.guide_page, self._total)

    def _forget_guide(self, project: Project) -> None:
        """The file is gone, so the project behaves as one without guide (RF-9)."""
        project.guide_file = None

    def _refresh(self) -> None:
        has_guide = self._document is not None
        self.attach_button.setVisible(not has_guide)
        self.notice_label.setVisible(not has_guide)
        self.previous_button.setVisible(has_guide)
        self.next_button.setVisible(has_guide)
        self.page_label.setVisible(has_guide)
        self.scroll.setVisible(has_guide)
        if not has_guide or self._project is None:
            self.image_label.clear()
            return
        page = self._project.guide_page
        self.page_label.setText(strings.PAGE.format(page=page, total=self._total))
        self.previous_button.setEnabled(page > 1)
        self.next_button.setEnabled(page < self._total)
        self._draw(page - 1)

    def _draw(self, index: int) -> None:
        # The label keeps the size of the page, so the scroll bars know how far they go.
        try:
            pixmap = render_page(self._document, index)
        except Exception:  # a single broken page must not block the rest (CL-14)
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(strings.PAGE_FAILED)
            self.image_label.setFixedSize(FAILED_SIZE, FAILED_SIZE)
            return
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(pixmap.size())
        self.scroll.verticalScrollBar().setValue(0)

    def _close(self) -> None:
        if self._document is not None:
            self._document.close()
        self._document = None
        self._total = 0
