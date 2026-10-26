"""Starting the app: no arguments, one window and the documented exit codes (RF-7, T33)."""

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from crochet_tracker import __main__ as entry
from crochet_tracker.presentation.main_window import MainWindow


@pytest.fixture
def data_folder(tmp_path, monkeypatch):
    """The app writes to a temporary folder, never to the real one of the user."""
    monkeypatch.setenv("CROCHET_TRACKER_DATA", str(tmp_path))
    return tmp_path


def test_without_arguments_it_starts_and_closes_normally(
    data_folder, qapp, monkeypatch
) -> None:
    shown: list[bool] = []
    monkeypatch.setattr(QApplication, "exec", lambda _app: 0)
    monkeypatch.setattr(MainWindow, "show", lambda window: shown.append(True))

    assert entry.main([]) == 0
    assert shown == [True]


def test_an_unknown_argument_writes_one_line_and_exits_with_2(data_folder, capsys) -> None:
    assert entry.main(["--help"]) == 2

    assert capsys.readouterr().err.strip() == "crochet_tracker: argumento no reconocido: --help"


def test_a_corrupt_database_exits_with_1_and_leaves_a_log(
    data_folder, qapp, capsys
) -> None:
    (data_folder / "crochet.db").write_bytes(b"esto no es una base de datos")

    assert entry.main([]) == 1

    assert capsys.readouterr().err.startswith("crochet_tracker: ")
    assert (data_folder / "error.log").is_file()


def test_a_database_from_a_newer_version_exits_with_1(data_folder, qapp, capsys) -> None:
    import sqlite3

    with sqlite3.connect(data_folder / "crochet.db") as connection:
        connection.execute("PRAGMA user_version = 99")

    assert entry.main([]) == 1

    assert capsys.readouterr().err.startswith("crochet_tracker: ")
    assert (data_folder / "error.log").is_file()


class _LockedElsewhere:
    """Stands for a lock another process already holds.

    In one process `QLockFile` hands over a lock it owns itself, so the real lock cannot
    simulate a second window; T32 covers it with a separate file handle.
    """

    def __init__(self, *_args) -> None:
        pass

    def acquire(self) -> bool:
        return False


def test_a_second_instance_warns_and_exits_with_0(
    data_folder, qapp, monkeypatch
) -> None:
    monkeypatch.setattr(entry, "SingleInstance", _LockedElsewhere)
    monkeypatch.setattr(QApplication, "exec", lambda _app: pytest.fail("no event loop"))
    warnings: list[tuple] = []
    monkeypatch.setattr(QMessageBox, "information", lambda *args: warnings.append(args))

    assert entry.main([]) == 0

    assert warnings
