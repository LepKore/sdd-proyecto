"""The guide PDF lives next to the database, not inside it (RF-8, RF-9).

A copy is made into a temporary file and moved into place at the end, so an
interrupted copy never leaves a half file (CL-11). Only the file name is
returned; the database stores that name and nothing else (plan, 2.1).
"""

import os
import shutil
import uuid
from pathlib import Path

import pypdfium2 as pdfium

from crochet_tracker.application.errors import GuideError
from crochet_tracker.infrastructure.app_paths import GUIDES_DIR_NAME, data_dir

__all__ = ["GuideError", "GuideStore"]


def _check_readable(path: Path) -> None:
    # PDFium refuses both damaged files and documents with no pages (CL-12, CL-13).
    try:
        document = pdfium.PdfDocument(str(path))
    except pdfium.PdfiumError as error:
        raise GuideError("El archivo no es un PDF legible") from error
    document.close()


class GuideStore:
    """Copies guides into the data folder and finds them back."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._dir = (base_dir or data_dir()) / GUIDES_DIR_NAME

    def copy(self, project_id: int, source: Path) -> str:
        """Store a copy of `source` and return its file name.

        Raises `GuideError` when the file is gone (CL-10) or cannot be read
        (CL-12, CL-13); in that case nothing is stored.
        """
        source = Path(source)
        if not source.is_file():
            raise GuideError(f"No se encuentra el archivo: {source.name}")
        _check_readable(source)
        self._dir.mkdir(parents=True, exist_ok=True)
        target = self._dir / f"{project_id}-{uuid.uuid4().hex}.pdf"
        partial = target.with_suffix(".part")
        try:
            shutil.copyfile(source, partial)
            os.replace(partial, target)
        except OSError as error:
            # A leftover .part is inert: it is never looked up as a guide.
            partial.unlink(missing_ok=True)
            raise GuideError("No se pudo copiar la guía") from error
        return target.name

    def path(self, name: str | None) -> Path | None:
        """Where the stored guide is, or None when it is missing (CL-9)."""
        if not name:
            return None
        stored = self._dir / Path(name).name
        return stored if stored.is_file() else None
