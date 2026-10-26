"""Notes of the open project: add, edit with Save/Cancel, delete (RF-14, RF-15)."""

from datetime import datetime
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.notes import add_note, delete_note, edit_note
from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.errors import EmptyNoteText
from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project
from crochet_tracker.domain.undo import Undo
from crochet_tracker.presentation import strings


def confirm_delete_note(parent: QWidget) -> bool:
    """Ask before removing the selected note (RF-15)."""
    box = QMessageBox(parent)
    box.setWindowTitle(strings.DELETE_NOTE)
    box.setText(strings.CONFIRM_DELETE_NOTE)
    delete_button = box.addButton(strings.DELETE_NOTE, QMessageBox.ButtonRole.AcceptRole)
    box.addButton(strings.CANCEL, QMessageBox.ButtonRole.RejectRole)
    box.exec()
    return box.clickedButton() is delete_button


class NotesPanel(QWidget):
    """Newest note on top; reading from the repository is the only source of truth."""

    def __init__(
        self,
        repository: ProjectRepository,
        clock: Clock,
        undo: Undo,
        on_change: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repository = repository
        self._clock = clock
        self._undo = undo
        self._on_change = on_change
        self._project: Project | None = None
        self._notes: list[Note] = []

        self.new_text = QPlainTextEdit()
        self.new_text.setPlaceholderText(strings.NOTES)
        self.add_button = QPushButton(strings.ADD_NOTE)
        self.notes_list = QListWidget()
        self.edit_text = QPlainTextEdit()
        self.save_button = QPushButton(strings.SAVE)
        self.cancel_button = QPushButton(strings.CANCEL)
        self.delete_button = QPushButton(strings.DELETE_NOTE)

        layout = QVBoxLayout(self)
        layout.addWidget(self.new_text)
        layout.addWidget(self.add_button)
        layout.addWidget(self.notes_list, 1)
        layout.addWidget(self.edit_text)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.delete_button)

        self.add_button.clicked.connect(lambda: self.add())
        self.save_button.clicked.connect(lambda: self.save())
        self.cancel_button.clicked.connect(lambda: self.cancel())
        self.delete_button.clicked.connect(lambda: self.delete())
        self.notes_list.currentRowChanged.connect(lambda _row: self._load_selected())
        self._set_editable(False)

    def set_project(self, project: Project) -> None:
        """Show the notes stored for this project (RF-14)."""
        self._project = project
        self.new_text.clear()
        self.refresh()

    def refresh(self, select_id: int | None = None) -> None:
        """Reload from the repository, newest first."""
        if self._project is None:
            return
        self._notes = self._repository.list_notes(self._project.id)
        self.notes_list.clear()
        for note in self._notes:
            item = QListWidgetItem(f"{_format(note.created_at)}\n{note.body}")
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            self.notes_list.addItem(item)
            if note.id == select_id:
                self.notes_list.setCurrentItem(item)
        self._load_selected()

    def add(self) -> None:
        """Store a new note with the system date; a blank text warns (RF-14, CL-19)."""
        if self._project is None:
            return
        try:
            add_note(
                self._repository,
                self._clock,
                self._project,
                self.new_text.toPlainText(),
                self._undo,
            )
        except EmptyNoteText:
            QMessageBox.warning(self, strings.NOTES, strings.NOTE_REQUIRED)
            return
        except SaveFailed:
            QMessageBox.warning(self, strings.NOTES, strings.SAVE_FAILED)
            return
        self.new_text.clear()
        self.refresh()
        self._on_change()

    def save(self) -> None:
        """Write the edited text keeping the creation date; blank keeps the old text (RF-15)."""
        note = self._current()
        if note is None:
            return
        try:
            edit_note(
                self._repository, self._clock, note, self.edit_text.toPlainText(), self._undo
            )
        except EmptyNoteText:
            QMessageBox.warning(self, strings.NOTES, strings.NOTE_REQUIRED)
            self.cancel()
            return
        except SaveFailed:
            QMessageBox.warning(self, strings.NOTES, strings.SAVE_FAILED)
            return
        self.refresh(select_id=note.id)
        self._on_change()

    def cancel(self) -> None:
        """Throw the edit away and show the saved text again (RF-15, CL-23)."""
        self._load_selected()

    def delete(self) -> None:
        """Remove the selected note only after the user confirms (RF-15)."""
        note = self._current()
        if note is None or self._project is None:
            return
        if not confirm_delete_note(self):
            return
        try:
            delete_note(self._repository, self._clock, self._project, note, self._undo)
        except SaveFailed:
            QMessageBox.warning(self, strings.NOTES, strings.SAVE_FAILED)
            return
        self.refresh()
        self._on_change()

    def _current(self) -> Note | None:
        item = self.notes_list.currentItem()
        if item is None:
            return None
        note_id = item.data(Qt.ItemDataRole.UserRole)
        return next((note for note in self._notes if note.id == note_id), None)

    def _load_selected(self) -> None:
        note = self._current()
        self._set_editable(note is not None)
        self.edit_text.setPlainText(note.body if note is not None else "")

    def _set_editable(self, editable: bool) -> None:
        self.edit_text.setEnabled(editable)
        self.save_button.setEnabled(editable)
        self.cancel_button.setEnabled(editable)
        self.delete_button.setEnabled(editable)


def _format(created_at: int) -> str:
    return datetime.fromtimestamp(created_at).strftime("%d/%m/%Y %H:%M")
