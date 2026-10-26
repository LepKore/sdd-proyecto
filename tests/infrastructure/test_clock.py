import time

from crochet_tracker.domain.undo import Undo
from crochet_tracker.infrastructure.clock import SystemClock


def test_now_returns_whole_seconds_of_the_system_clock():
    now = SystemClock().now()

    assert isinstance(now, int)
    assert abs(now - time.time()) <= 2


def test_a_fake_with_the_same_shape_drives_the_undo_window():
    class FakeClock:
        def __init__(self) -> None:
            self.seconds = 1_000

        def now(self) -> int:
            return self.seconds

    clock = FakeClock()
    undo = Undo()

    def plus_one() -> None:
        pass

    undo.remember(plus_one, clock.now())
    clock.seconds += 600
    assert undo.is_available(clock.now())
    clock.seconds += 1
    assert not undo.is_available(clock.now())
