"""List of projects: open, create and delete from here (RF-1, RF-2, RF-3, RF-6)."""

from datetime import datetime
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from crochet_tracker.application.create_project import create_project
from crochet_tracker.application.delete_project import delete_project
from crochet_tracker.application.list_projects import list_projects
from crochet_tracker.domain.errors import InvalidProjectName
from crochet_tracker.domain.project import MAX_NAME_LENGTH, Project
from crochet_tracker.presentation import strings


def ask_project_name(parent: QWidget) -> tuple[str, bool]:
    """Ask for the name; the text box stops at MAX_NAME_LENGTH (RF-1)."""
    dialog = QInputDialog(parent)
    dialog.setWindowTitle(strings.NEW_PROJECT)
    dialog.setLabelText(strings.PROJECT_NAME)
    dialog.setOkButtonText(strings.OK)
    dialog.setCancelButtonText(strings.CANCEL)
    text_box = dialog.findChild(QLineEdit)
    if text_box is not None:
        text_box.setMaxLength(MAX_NAME_LENGTH)
    accepted = dialog.exec() == QInputDialog.DialogCode.Accepted
    return dialog.textValue(), accepted


def confirm_delete(parent: QWidget, name: str) -> bool:
    """Ask before losing the project for good, showing its name (RF-6)."""
    box = QMessageBox(parent)
    box.setWindowTitle(strings.DELETE_PROJECT)
    box.setText(strings.CONFIRM_DELETE.format(name=name))
    delete_button = box.addButton(strings.DELETE, QMessageBox.ButtonRole.AcceptRole)
    box.addButton(strings.CANCEL, QMessageBox.ButtonRole.RejectRole)
    box.exec()
    return box.clickedButton() is delete_button


class ProjectListView(QWidget):
    """One row per project, newest first; the same row is where it can be deleted."""

    def __init__(
        self,
        repository,
        clock,
        on_open: Callable[[Project], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repository = repository
        self._clock = clock
        self._on_open = on_open
        self._projects: list[Project] = []

        self.empty_label = QLabel(strings.EMPTY_LIST)
        self.list_widget = QListWidget()
        self.list_widget.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.new_button = QPushButton(strings.NEW_PROJECT)
        self.delete_button = QPushButton(strings.DELETE_PROJECT)

        buttons = QVBoxLayout()
        buttons.addWidget(self.new_button)
        buttons.addWidget(self.delete_button)
        buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.list_widget, 1)
        layout.addLayout(buttons)

        self.new_button.clicked.connect(lambda: self.create())
        self.delete_button.clicked.connect(lambda: self.delete())
        self.list_widget.itemActivated.connect(lambda _item: self.open_selected())

        self.refresh()

    def refresh(self) -> None:
        """Rebuild the rows from the repository, newest modification on top."""
        self._projects = list_projects(self._repository)
        self.list_widget.clear()
        for project in self._projects:
            item = QListWidgetItem(self._row_text(project))
            item.setData(Qt.ItemDataRole.UserRole, project.id)
            item.setToolTip(project.name)
            self.list_widget.addItem(item)
        self.empty_label.setVisible(not self._projects)
        self.list_widget.setVisible(bool(self._projects))
        if self._projects:
            self.list_widget.setCurrentRow(0)

    def create(self) -> None:
        """Create the project and open it; a blank name changes nothing (CL-1)."""
        name, accepted = ask_project_name(self)
        if not accepted:
            return
        try:
            project = create_project(self._repository, self._clock, name)
        except InvalidProjectName:
            QMessageBox.warning(self, strings.NEW_PROJECT, strings.NAME_REQUIRED)
            return
        self._on_open(project)

    def open_selected(self) -> None:
        project = self._current()
        if project is not None:
            self._on_open(project)

    def delete(self) -> None:
        """Delete only after the user confirms, naming the project (RF-6)."""
        project = self._current()
        if project is None or project.id is None:
            return
        if not confirm_delete(self, project.name):
            return
        delete_project(self._repository, project.id)
        self.refresh()

    def _current(self) -> Project | None:
        item = self.list_widget.currentItem()
        if item is None and self.list_widget.count():
            self.list_widget.setCurrentRow(0)
            item = self.list_widget.currentItem()
        if item is None:
            return None
        project_id = item.data(Qt.ItemDataRole.UserRole)
        return next((p for p in self._projects if p.id == project_id), None)

    @staticmethod
    def _row_text(project: Project) -> str:
        changed = datetime.fromtimestamp(project.updated_at).strftime("%d/%m/%Y %H:%M")
        label = f" — {strings.FINISHED}" if project.is_finished else ""
        return f"{project.name}{label}   ({changed})"
