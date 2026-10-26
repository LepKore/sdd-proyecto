import pathlib

import pytest

from crochet_tracker.domain.errors import InvalidProjectName
from crochet_tracker.domain.project import MAX_NAME_LENGTH, normalize_name

DOMAIN_DIR = pathlib.Path(__file__).resolve().parents[2] / "crochet_tracker" / "domain"


def test_edges_are_trimmed():
    assert normalize_name("  Bufanda de lana \n") == "Bufanda de lana"


def test_inner_text_is_kept_as_typed():
    name = "Bufanda  \t de 🧶 lana"
    assert normalize_name(f"  {name}  ") == name


@pytest.mark.parametrize("name", ["", " ", "   \t\n "])
def test_empty_or_blank_is_rejected(name):
    with pytest.raises(InvalidProjectName):
        normalize_name(name)


def test_100_characters_are_accepted():
    name = "a" * MAX_NAME_LENGTH
    assert normalize_name(name) == name


def test_more_than_100_characters_are_rejected():
    with pytest.raises(InvalidProjectName):
        normalize_name("a" * (MAX_NAME_LENGTH + 1))


def test_limit_counts_the_trimmed_name():
    assert normalize_name("  " + "a" * MAX_NAME_LENGTH + "  ") == "a" * MAX_NAME_LENGTH


def test_repeated_names_are_allowed():
    assert normalize_name("Bufanda") == normalize_name("Bufanda")


def test_domain_does_not_import_outer_layers():
    forbidden = ("PySide6", "pypdfium2", "sqlite3", "pathlib")
    for path in DOMAIN_DIR.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for module in forbidden:
            assert f"import {module}" not in source, f"{path.name} imports {module}"
