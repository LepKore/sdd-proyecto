import pytest

from crochet_tracker.domain.errors import EmptyNoteText
from crochet_tracker.domain.note import Note

CREATED_AT = 1_761_400_000


def test_note_keeps_body_and_creation_time():
    note = Note("Fila 3: cambiar a aguja de 4 mm", CREATED_AT)
    assert note.body == "Fila 3: cambiar a aguja de 4 mm"
    assert note.created_at == CREATED_AT


@pytest.mark.parametrize("body", ["", " ", "   \t\n "])
def test_empty_or_blank_text_is_rejected(body):
    with pytest.raises(EmptyNoteText):
        Note(body, CREATED_AT)


def test_editing_replaces_the_text():
    note = Note("primera", CREATED_AT)
    note.edit("segunda")
    assert note.body == "segunda"


def test_editing_keeps_the_original_creation_time():
    note = Note("primera", CREATED_AT)
    note.edit("segunda")
    assert note.created_at == CREATED_AT


def test_editing_to_blank_is_rejected_and_keeps_the_old_text():
    note = Note("primera", CREATED_AT)
    with pytest.raises(EmptyNoteText):
        note.edit("   ")
    assert note.body == "primera"


def test_multiline_text_is_kept_as_typed():
    body = "vuelta 4:\n  - 2 juntos\n  - hebra"
    assert Note(body, CREATED_AT).body == body
