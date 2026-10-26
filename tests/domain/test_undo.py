from crochet_tracker.domain.project import Project
from crochet_tracker.domain.undo import UNDO_WINDOW_SECONDS, Undo

NOW = 1_761_400_000


def test_nothing_is_available_before_any_change():
    undo = Undo()
    assert undo.is_available(NOW) is False
    assert undo.take(NOW) is None


def test_a_remembered_change_is_available():
    undo = Undo()
    undo.remember(lambda: None, NOW)
    assert undo.is_available(NOW) is True


def test_the_window_is_ten_minutes():
    assert UNDO_WINDOW_SECONDS == 600


def test_the_change_is_still_available_at_the_edge_of_the_window():
    undo = Undo()
    undo.remember(lambda: None, NOW)
    assert undo.is_available(NOW + UNDO_WINDOW_SECONDS) is True


def test_the_change_expires_after_the_window():
    undo = Undo()
    undo.remember(lambda: None, NOW)
    assert undo.is_available(NOW + UNDO_WINDOW_SECONDS + 1) is False
    assert undo.take(NOW + UNDO_WINDOW_SECONDS + 1) is None


def test_only_the_latest_change_can_be_undone():
    undo = Undo()
    undo.remember(lambda: "first", NOW)
    undo.remember(lambda: "second", NOW)
    assert undo.take(NOW)() == "second"


def test_taking_the_change_forgets_it():
    undo = Undo()
    undo.remember(lambda: None, NOW)
    undo.take(NOW)
    assert undo.is_available(NOW) is False
    assert undo.take(NOW) is None


def test_there_is_no_redo():
    assert not hasattr(Undo(), "redo")


def test_discarding_drops_the_pending_change():
    undo = Undo()
    undo.remember(lambda: None, NOW)
    undo.discard()
    assert undo.is_available(NOW) is False


def test_changes_that_cannot_be_undone_do_not_drop_the_pending_one():
    project = Project("Bufanda", rows_done=1)
    undo = Undo()
    undone = []
    undo.remember(lambda: undone.append("counter"), NOW)

    project.name = "Bufanda larga"
    project.toggle_finished()
    project.change_page(1, total_pages=10)

    assert undo.is_available(NOW) is True
    undo.take(NOW)()
    assert undone == ["counter"]
