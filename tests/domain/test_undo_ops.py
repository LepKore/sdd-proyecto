from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project
from crochet_tracker.domain.undo import Undo

NOW = 1_761_400_000


def change_rows(project: Project, delta: int) -> Undo:
    """Change a counter the way the application does: remember the previous value."""
    undo = Undo()
    previous = project.rows_done
    project.change_rows(delta)
    undo.remember(lambda: project.restore_rows(previous), NOW)
    return undo


def test_undoing_a_counter_restores_the_previous_value():
    project = Project("Bufanda", rows_done=3)
    undo = change_rows(project, 1)
    assert project.rows_done == 4

    undo.take(NOW)()

    assert project.rows_done == 3


def test_undoing_a_decrement_restores_the_previous_value():
    project = Project("Bufanda", rows_done=5)
    undo = change_rows(project, -1)
    assert project.rows_done == 4

    undo.take(NOW)()

    assert project.rows_done == 5


def test_undoing_the_deletion_of_a_note_restores_text_and_date():
    notes = [Note("fila 3: 2 juntos", 1_761_300_000)]
    undo = Undo()
    deleted = notes.pop(0)
    undo.remember(lambda: notes.insert(0, deleted), NOW)

    undo.take(NOW)()

    assert [note.body for note in notes] == ["fila 3: 2 juntos"]
    assert notes[0].created_at == 1_761_300_000


def test_undoing_the_edition_of_a_note_restores_the_previous_text_and_date():
    note = Note("fila 3", 1_761_300_000)
    undo = Undo()
    previous_body = note.body
    note.edit("fila 4")
    undo.remember(lambda: note.edit(previous_body), NOW)

    undo.take(NOW)()

    assert note.body == "fila 3"
    assert note.created_at == 1_761_300_000


def test_undoing_is_not_itself_undoable():
    project = Project("Bufanda", rows_done=1)
    undo = change_rows(project, 1)
    undo.take(NOW)()

    assert undo.take(NOW) is None
    assert project.rows_done == 1
