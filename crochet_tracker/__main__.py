"""Entry point: no arguments, one window, and an exit code for every failure (RF-7).

Exit codes follow plan §3.2: 0 normal or already running, 1 fatal error, 2 unknown argument.
"""

import sqlite3
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from crochet_tracker.infrastructure.app_paths import DB_FILE_NAME, ERROR_LOG_NAME, data_dir
from crochet_tracker.infrastructure.clock import SystemClock
from crochet_tracker.infrastructure.guide_store import GuideStore
from crochet_tracker.infrastructure.migrations import MigrationError
from crochet_tracker.infrastructure.single_instance import SingleInstance
from crochet_tracker.infrastructure.sqlite_repository import SqliteProjectRepository
from crochet_tracker.presentation import strings
from crochet_tracker.presentation.main_window import MainWindow

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_BAD_ARGUMENTS = 2
MESSAGE_PREFIX = "crochet_tracker: "


def main(argv: list[str] | None = None) -> int:
    """Start the application; the only supported form is without arguments."""
    arguments = sys.argv[1:] if argv is None else argv
    if arguments:
        return _complain(f"argumento no reconocido: {arguments[0]}", EXIT_BAD_ARGUMENTS)

    app = QApplication.instance() or QApplication(sys.argv[:1])
    try:
        data = data_dir()
        repository = SqliteProjectRepository(data / DB_FILE_NAME)
    except (sqlite3.DatabaseError, MigrationError, OSError) as error:
        return _fatal(error)

    instance = SingleInstance(data)
    if not instance.acquire():
        QMessageBox.information(None, strings.APP_TITLE, strings.ALREADY_RUNNING)
        return EXIT_OK

    window = MainWindow(repository, SystemClock(), GuideStore())
    window.show()
    return app.exec()


def _fatal(error: Exception) -> int:
    """Report the reason on stderr and in error.log, where --windowed can still be read."""
    print(MESSAGE_PREFIX + str(error), file=sys.stderr)
    try:
        log = data_dir() / ERROR_LOG_NAME
        log.write_text("".join(traceback.format_exception(error)), encoding="utf-8")
    except OSError:
        pass
    return EXIT_FAILED


def _complain(message: str, code: int) -> int:
    print(MESSAGE_PREFIX + message, file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
