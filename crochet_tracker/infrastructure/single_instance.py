"""Only one copy of the application at a time over the same data (RF-7, CL-29).

`QLockFile` already comes with PySide6, notices a lock left behind by a crashed run and
works on the three platforms (plan §4.3).
"""

from pathlib import Path

from PySide6.QtCore import QLockFile

from crochet_tracker.infrastructure.app_paths import LOCK_FILE_NAME, data_dir


class SingleInstance:
    """The first process gets the lock; the second one is told to stop."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._lock = QLockFile(str((base_dir or data_dir()) / LOCK_FILE_NAME))

    def acquire(self) -> bool:
        """Return True only for the first process; a stale lock is taken over."""
        return self._lock.tryLock(0)

    def release(self) -> None:
        """Give the lock back so the next start is a normal one."""
        self._lock.unlock()
