"""Undo the last undoable change, one step and ten minutes at most (RF-16)."""

from crochet_tracker.application.ports import Clock
from crochet_tracker.domain.undo import Undo


def can_undo(undo: Undo, clock: Clock) -> bool:
    """Whether the control has to be offered: there is a change and it is still fresh (RF-16)."""
    return undo.is_available(clock.now())


def undo_last_change(clock: Clock, undo: Undo) -> bool:
    """Apply the pending inverse, forget it and return True, or return False if there is none.

    Undoing is not itself undoable: the inverse is applied and the entry is gone (RF-16).
    """
    inverse = undo.take(clock.now())
    if inverse is None:
        return False
    inverse()
    return True
