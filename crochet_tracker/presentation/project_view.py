"""Screen of one open project: name, state, counters, notes and undo (RF-3..RF-16)."""

from typing import Callable

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from crochet_tracker.application.counters import add_knots, add_rows, remove_knots, remove_rows
from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, GuideStore, ProjectRepository
from crochet_tracker.application.rename_project import rename_project
from crochet_tracker.application.set_finished import set_finished
from crochet_tracker.application.undo_last_change import can_undo, undo_last_change
from crochet_tracker.domain.errors import InvalidProjectName
from crochet_tracker.domain.project import Project
from crochet_tracker.domain.undo import Undo
from crochet_tracker.presentation import strings
from crochet_tracker.presentation.guide_view import GuideView
from crochet_tracker.presentation.notes_panel import NotesPanel

CHECK_UNDO_EVERY_MS = 30_000


class ProjectView(QWidget):
    """One project at a time: editing it here saves at once, without a save button."""

    def __init__(
        self,
        repository: ProjectRepository,
        clock: Clock,
        guides: GuideStore,
        on_back: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repository = repository
        self._clock = clock
        self._on_back = on_back
        self._project: Project | None = None
        self.undo = Undo()

        self.back_button = QPushButton(strings.BACK_TO_PROJECTS)
        self.name_edit = QLineEdit()
        self.rename_button = QPushButton(strings.RENAME)
        self.finished_label = QLabel(strings.FINISHED)
        self.finished_button = QPushButton(strings.MARK_FINISHED)
        self.rows_label = QLabel()
        self.knots_label = QLabel()
        self.rows_down = QPushButton(strings.DECREASE)
        self.rows_up = QPushButton(strings.INCREASE)
        self.knots_down = QPushButton(strings.DECREASE)
        self.knots_up = QPushButton(strings.INCREASE)
        self.undo_label = QLabel(strings.UNDO_AVAILABLE)
        self.undo_button = QPushButton(strings.UNDO)
        self.guide_view = GuideView(repository, clock, guides)
        self.notes_panel = NotesPanel(repository, clock, self.undo, self._refresh_undo)

        name_row = QHBoxLayout()
        name_row.addWidget(self.name_edit, 1)
        name_row.addWidget(self.rename_button)

        state_row = QHBoxLayout()
        state_row.addWidget(self.finished_label, 1)
        state_row.addWidget(self.finished_button)

        undo_row = QHBoxLayout()
        undo_row.addWidget(self.undo_label, 1)
        undo_row.addWidget(self.undo_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.back_button)
        layout.addLayout(name_row)
        layout.addLayout(state_row)
        layout.addLayout(
            _counter_row(strings.ROWS, self.rows_label, self.rows_down, self.rows_up)
        )
        layout.addLayout(
            _counter_row(strings.KNOTS, self.knots_label, self.knots_down, self.knots_up)
        )
        layout.addLayout(undo_row)
        layout.addWidget(self.guide_view, 2)
        layout.addWidget(self.notes_panel, 1)

        self._undo_timer = QTimer(self)
        self._undo_timer.setInterval(CHECK_UNDO_EVERY_MS)
        self._undo_timer.timeout.connect(self._refresh_undo)
        self._undo_timer.start()

        self.back_button.clicked.connect(lambda: self._on_back())
        self.rename_button.clicked.connect(lambda: self.rename())
        self.finished_button.clicked.connect(lambda: self.toggle_finished())
        self.undo_button.clicked.connect(lambda: self.undo_last())
        self.rows_up.clicked.connect(lambda: self._count(add_rows))
        self.rows_down.clicked.connect(lambda: self._count(remove_rows))
        self.knots_up.clicked.connect(lambda: self._count(add_knots))
        self.knots_down.clicked.connect(lambda: self._count(remove_knots))

    def set_project(self, project: Project) -> None:
        """Show the values saved for this project and forget any pending undo (RF-3, RF-16)."""
        self.undo.discard()
        self._project = project
        self.name_edit.setText(project.name)
        self.guide_view.set_project(project)
        self.notes_panel.set_project(project)
        self.refresh()

    def refresh(self) -> None:
        """Paint every value from the project and the undo state."""
        if self._project is None:
            return
        project = self._project
        self.name_edit.setText(project.name)
        self.finished_label.setVisible(project.is_finished)
        self.finished_button.setText(
            strings.MARK_UNFINISHED if project.is_finished else strings.MARK_FINISHED
        )
        self.rows_label.setText(str(project.rows_done))
        self.knots_label.setText(str(project.knots_done))
        self.rows_down.setEnabled(project.rows_done > 0)
        self.knots_down.setEnabled(project.knots_done > 0)
        self._refresh_undo()

    def rename(self) -> None:
        """Store the typed name; a blank one warns and keeps the previous (RF-4, CL-1)."""
        if self._project is None:
            return
        try:
            rename_project(
                self._repository, self._clock, self._project, self.name_edit.text()
            )
        except InvalidProjectName:
            QMessageBox.warning(self, strings.RENAME, strings.NAME_REQUIRED)
        except SaveFailed:
            QMessageBox.warning(self, strings.APP_TITLE, strings.SAVE_FAILED)
        self.refresh()

    def toggle_finished(self) -> None:
        """Swap finished and in progress, saving at once (RF-5)."""
        if self._project is None:
            return
        try:
            set_finished(self._repository, self._clock, self._project)
        except SaveFailed:
            QMessageBox.warning(self, strings.APP_TITLE, strings.SAVE_FAILED)
        self.refresh()

    def undo_last(self) -> None:
        """Apply the pending inverse; undoing is not itself undoable (RF-16)."""
        try:
            undo_last_change(self._clock, self.undo)
        except SaveFailed:
            QMessageBox.warning(self, strings.APP_TITLE, strings.SAVE_FAILED)
        self.notes_panel.refresh()
        self.refresh()

    def discard_undo(self) -> None:
        """Forget the pending undo when leaving the project (RF-16)."""
        self.undo.discard()
        self._refresh_undo()

    def _count(self, action) -> None:
        """Save at once; a failed save warns and keeps the previous value (RF-13)."""
        if self._project is None:
            return
        try:
            action(self._repository, self._clock, self._project, self.undo)
        except SaveFailed:
            QMessageBox.warning(self, strings.APP_TITLE, strings.SAVE_FAILED)
        self.refresh()

    def _refresh_undo(self) -> None:
        """Offer undo only while the change exists and is fresh (RF-16)."""
        available = self._project is not None and can_undo(self.undo, self._clock)
        self.undo_label.setVisible(available)
        self.undo_button.setVisible(available)


def _counter_row(name: str, value: QLabel, down: QPushButton, up: QPushButton) -> QHBoxLayout:
    row = QHBoxLayout()
    row.addWidget(QLabel(name))
    row.addWidget(value, 1)
    row.addWidget(down)
    row.addWidget(up)
    return row
