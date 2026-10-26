"""Screen of one open project: counters and notes (RF-3, RF-11, RF-12, RF-13, RF-14, RF-15)."""

from typing import Callable

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from crochet_tracker.application.counters import add_knots, add_rows, remove_knots, remove_rows
from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.project import Project
from crochet_tracker.domain.undo import Undo
from crochet_tracker.presentation import strings
from crochet_tracker.presentation.notes_panel import NotesPanel


class ProjectView(QWidget):
    """Shows which project is open, its two counters and its notes."""

    def __init__(
        self,
        repository: ProjectRepository,
        clock: Clock,
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
        self.name_label = QLabel()
        self.rows_label = QLabel()
        self.knots_label = QLabel()
        self.rows_down = QPushButton(strings.DECREASE)
        self.rows_up = QPushButton(strings.INCREASE)
        self.knots_down = QPushButton(strings.DECREASE)
        self.knots_up = QPushButton(strings.INCREASE)
        self.notes_panel = NotesPanel(repository, clock, self.undo)

        layout = QVBoxLayout(self)
        layout.addWidget(self.back_button)
        layout.addWidget(self.name_label)
        layout.addLayout(
            _counter_row(strings.ROWS, self.rows_label, self.rows_down, self.rows_up)
        )
        layout.addLayout(
            _counter_row(strings.KNOTS, self.knots_label, self.knots_down, self.knots_up)
        )
        layout.addWidget(self.notes_panel, 1)

        self.back_button.clicked.connect(lambda: self._on_back())
        self.rows_up.clicked.connect(lambda: self._count(add_rows))
        self.rows_down.clicked.connect(lambda: self._count(remove_rows))
        self.knots_up.clicked.connect(lambda: self._count(add_knots))
        self.knots_down.clicked.connect(lambda: self._count(remove_knots))

    def set_project(self, project: Project) -> None:
        """Show the values saved for this project (RF-3)."""
        self._project = project
        self.name_label.setText(project.name)
        self.notes_panel.set_project(project)
        self.refresh()

    def refresh(self) -> None:
        """Paint the counters and disable going below zero (RF-12, CL-17)."""
        if self._project is None:
            return
        self.rows_label.setText(str(self._project.rows_done))
        self.knots_label.setText(str(self._project.knots_done))
        self.rows_down.setEnabled(self._project.rows_done > 0)
        self.knots_down.setEnabled(self._project.knots_done > 0)

    def _count(self, action) -> None:
        """Save at once; a failed save warns and keeps the previous value (RF-13)."""
        if self._project is None:
            return
        try:
            action(self._repository, self._clock, self._project, self.undo)
        except SaveFailed:
            QMessageBox.warning(self, strings.APP_TITLE, strings.SAVE_FAILED)
        self.refresh()


def _counter_row(name: str, value: QLabel, down: QPushButton, up: QPushButton) -> QHBoxLayout:
    row = QHBoxLayout()
    row.addWidget(QLabel(name))
    row.addWidget(value, 1)
    row.addWidget(down)
    row.addWidget(up)
    return row
