from pathlib import Path

import pytest

from crochet_tracker.infrastructure import guide_store
from crochet_tracker.infrastructure.guide_store import GuideError, GuideStore

# One page, no page content: PDFium opens it, which is all the store asks.
MINIMAL_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>
endobj
trailer
<< /Root 1 0 R /Size 4 >>
%%EOF
"""

# Valid structure, zero pages: PDFium rejects it before counting (CL-13).
EMPTY_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [] /Count 0 >>
endobj
trailer
<< /Root 1 0 R /Size 3 >>
%%EOF
"""


@pytest.fixture
def store(tmp_path):
    return GuideStore(tmp_path)


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "patron.pdf"
    path.write_bytes(MINIMAL_PDF)
    return path


def test_copy_stores_the_file_and_returns_its_name(store, source, tmp_path):
    name = store.copy(7, source)

    assert name.startswith("7-") and name.endswith(".pdf")
    stored = tmp_path / "guides" / name
    assert stored.read_bytes() == MINIMAL_PDF


def test_the_copy_survives_deleting_the_original(store, source):
    name = store.copy(7, source)
    source.unlink()

    assert store.path(name).is_file()


def test_each_copy_gets_its_own_name(store, source):
    assert store.copy(7, source) != store.copy(7, source)


def test_a_missing_guide_is_reported_as_no_guide(store):
    assert store.path(None) is None
    assert store.path("3-borrada.pdf") is None


def test_the_name_cannot_reach_outside_the_guides_folder(store):
    assert store.path("../suelto.pdf") is None


def test_a_file_that_is_not_a_pdf_is_rejected(store, tmp_path):
    junk = tmp_path / "notas.txt"
    junk.write_text("no soy un PDF")

    with pytest.raises(GuideError):
        store.copy(3, junk)
    assert not (tmp_path / "guides").exists() or not list(
        (tmp_path / "guides").iterdir()
    )


def test_a_pdf_with_no_pages_is_rejected(store, tmp_path):
    empty = tmp_path / "vacio.pdf"
    empty.write_bytes(EMPTY_PDF)

    with pytest.raises(GuideError):
        store.copy(3, empty)


def test_a_source_that_disappeared_first_leaves_no_guide(store, tmp_path):
    with pytest.raises(GuideError):
        store.copy(3, tmp_path / "movido.pdf")
    assert not (tmp_path / "guides").exists() or not list(
        (tmp_path / "guides").iterdir()
    )


def test_an_interrupted_copy_leaves_no_half_file(store, source, tmp_path, monkeypatch):
    def interrupted(source, target, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4")
        raise OSError("se corto la copia")

    monkeypatch.setattr(guide_store.shutil, "copyfile", interrupted)

    with pytest.raises(GuideError):
        store.copy(3, source)
    assert list((tmp_path / "guides").iterdir()) == []
