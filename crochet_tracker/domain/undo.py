"""One-step undo with a time window (RF-16).

The inverse operation is a plain callable, so the domain never needs to know
whether it is restoring a counter or a note: the application builds it.
There is no redo and no history: one entry, and it is gone once used (RF-16).
"""

from collections.abc import Callable
from dataclasses import dataclass, field

UNDO_WINDOW_SECONDS = 10 * 60


@dataclass
class Undo:
    _inverse: Callable[[], None] | None = field(default=None, init=False)
    _recorded_at: int = field(default=0, init=False)

    def remember(self, inverse: Callable[[], None], now: int) -> None:
        """Keep the inverse of the latest undoable change, replacing any pending one."""
        self._inverse = inverse
        self._recorded_at = now

    def is_available(self, now: int) -> bool:
        return self._inverse is not None and now - self._recorded_at <= UNDO_WINDOW_SECONDS

    def take(self, now: int) -> Callable[[], None] | None:
        """Return the pending inverse and forget it, or return None when there is none."""
        if not self.is_available(now):
            self.discard()
            return None
        inverse = self._inverse
        self.discard()
        return inverse

    def discard(self) -> None:
        self._inverse = None
