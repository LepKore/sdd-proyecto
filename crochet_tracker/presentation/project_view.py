"""Screen of one open project (RF-3). Counters, notes and guide arrive in T28-T31."""

from typing import Callable

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from crochet_tracker.domain.project import Project
from crochet_tracker.presentation import strings


class ProjectView(QWidget):
    """Shows which project is open and how to get back to the list."""

    def __init__(self, on_back: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_back = on_back
        self.name_label = QLabel()
        self.back_button = QPushButton(strings.BACK_TO_PROJECTS)

        layout = QVBoxLayout(self)
        layout.addWidget(self.back_button)
        layout.addWidget(self.name_label)
        layout.addStretch(1)

        self.back_button.clicked.connect(lambda: self._on_back())

    def set_project(self, project: Project) -> None:
        """Show the values saved for this project (RF-3)."""
        self.name_label.setText(project.name)
