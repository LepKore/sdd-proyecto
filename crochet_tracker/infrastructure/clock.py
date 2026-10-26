"""The real clock; tests substitute a fake one (RF-16)."""

import time


class SystemClock:
    """Seconds since the epoch, the unit the undo window uses."""

    def now(self) -> int:
        return int(time.time())
