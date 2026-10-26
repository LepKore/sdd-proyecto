"""Provisional entry point: wires the real adapters and opens the window.

Arguments and exit codes arrive with T33; until then it accepts no options (plan §3).
"""

import sys

from PySide6.QtWidgets import QApplication

from crochet_tracker.infrastructure.app_paths import DB_FILE_NAME, data_dir
from crochet_tracker.infrastructure.clock import SystemClock
from crochet_tracker.infrastructure.sqlite_repository import SqliteProjectRepository
from crochet_tracker.presentation.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    repository = SqliteProjectRepository(data_dir() / DB_FILE_NAME)
    window = MainWindow(repository, SystemClock())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
