"""Main window: one screen at a time, list or open project (RF-2, RF-3)."""

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget

from crochet_tracker.application.ports import Clock, GuideStore, ProjectRepository
from crochet_tracker.domain.project import Project
from crochet_tracker.presentation import strings
from crochet_tracker.presentation.project_list_view import ProjectListView
from crochet_tracker.presentation.project_view import ProjectView

DEFAULT_WIDTH = 1100
DEFAULT_HEIGHT = 800


class MainWindow(QMainWindow):
    """Switches between the list and the project screen; only one project is open."""

    def __init__(
        self,
        repository: ProjectRepository,
        clock: Clock,
        guides: GuideStore,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(strings.APP_TITLE)
        self.list_view = ProjectListView(repository, clock, self.open_project)
        self.project_view = ProjectView(repository, clock, guides, self.show_list)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.list_view)
        self.stack.addWidget(self.project_view)
        self.setCentralWidget(self.stack)

        self._fit_to_screen()
        self.show_list()

    def _fit_to_screen(self) -> None:
        """Start at a comfortable size, never larger than the screen (guides do not resize it)."""
        screen = QApplication.primaryScreen()
        if screen is None:  # headless test runs have no real screen
            self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
            return
        visible = screen.availableGeometry()
        self.resize(
            min(DEFAULT_WIDTH, visible.width()), min(DEFAULT_HEIGHT, visible.height())
        )

    def open_project(self, project: Project) -> None:
        """Open one project, closing whatever was open (RF-3)."""
        self.project_view.set_project(project)
        self.stack.setCurrentWidget(self.project_view)

    def show_list(self) -> None:
        """Go back to the list with every saved change visible (RF-3, RF-16)."""
        self.project_view.discard_undo()
        self.list_view.refresh()
        self.stack.setCurrentWidget(self.list_view)
