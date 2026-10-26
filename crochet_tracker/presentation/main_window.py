"""Main window: one screen at a time, list or open project (RF-2, RF-3)."""

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget

from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.project import Project
from crochet_tracker.presentation import strings
from crochet_tracker.presentation.project_list_view import ProjectListView
from crochet_tracker.presentation.project_view import ProjectView


class MainWindow(QMainWindow):
    """Switches between the list and the project screen; only one project is open."""

    def __init__(
        self,
        repository: ProjectRepository,
        clock: Clock,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(strings.APP_TITLE)
        self.list_view = ProjectListView(repository, clock, self.open_project)
        self.project_view = ProjectView(repository, clock, self.show_list)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.list_view)
        self.stack.addWidget(self.project_view)
        self.setCentralWidget(self.stack)

        self.show_list()

    def open_project(self, project: Project) -> None:
        """Open one project, closing whatever was open (RF-3)."""
        self.project_view.set_project(project)
        self.stack.setCurrentWidget(self.project_view)

    def show_list(self) -> None:
        """Go back to the list with every saved change visible (RF-3)."""
        self.list_view.refresh()
        self.stack.setCurrentWidget(self.list_view)
