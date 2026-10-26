"""Note use cases (RF-14, RF-15)."""

from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project
from crochet_tracker.domain.undo import Undo


def add_note(
    repository: ProjectRepository, clock: Clock, project: Project, body: str, undo: Undo
) -> Note:
    """Store a new note dated now and return it; a blank text raises EmptyNoteText (CL-19)."""
    note = Note(body=body, created_at=clock.now())
    try:
        note.id = repository.add_note(project.id, note)
    except Exception as error:
        raise SaveFailed("No se pudo guardar la nota") from error
    undo.remember(lambda: _remove(repository, note.id), clock.now())
    return note


def edit_note(
    repository: ProjectRepository, clock: Clock, note: Note, body: str, undo: Undo
) -> None:
    """Change only the text, keeping the creation date; a blank text keeps the old one (RF-15)."""
    previous = note.body
    note.edit(body)
    try:
        repository.save_note(note)
    except Exception as error:
        note.body = previous
        raise SaveFailed("No se pudo guardar la nota") from error
    undo.remember(lambda: _write_body(repository, note, previous), clock.now())


def delete_note(
    repository: ProjectRepository, clock: Clock, project: Project, note: Note, undo: Undo
) -> None:
    """Remove the note; the undo brings it back with its text and its original date (RF-16)."""
    try:
        repository.delete_note(note.id)
    except Exception as error:
        raise SaveFailed("No se pudo borrar la nota") from error
    undo.remember(
        lambda: _add_back(repository, project.id, note.body, note.created_at), clock.now()
    )


def _remove(repository: ProjectRepository, note_id: int) -> None:
    try:
        repository.delete_note(note_id)
    except Exception as error:
        raise SaveFailed("No se pudo deshacer el cambio") from error


def _write_body(repository: ProjectRepository, note: Note, body: str) -> None:
    current = note.body
    note.body = body
    try:
        repository.save_note(note)
    except Exception as error:
        note.body = current
        raise SaveFailed("No se pudo deshacer el cambio") from error


def _add_back(repository: ProjectRepository, project_id: int, body: str, created_at: int) -> None:
    try:
        repository.add_note(project_id, Note(body=body, created_at=created_at))
    except Exception as error:
        raise SaveFailed("No se pudo deshacer el cambio") from error
