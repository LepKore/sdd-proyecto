import pytest

from crochet_tracker.domain.project import Project


def test_counters_start_at_zero_and_independent():
    project = Project("Bufanda")
    assert (project.rows_done, project.knots_done) == (0, 0)

    project.change_rows(1)
    assert (project.rows_done, project.knots_done) == (1, 0)

    project.change_knots(1)
    assert (project.rows_done, project.knots_done) == (1, 1)


def test_decrement_reduces_the_counter():
    project = Project("Bufanda", rows_done=3, knots_done=5)
    project.change_rows(-1)
    project.change_knots(-1)
    assert (project.rows_done, project.knots_done) == (2, 4)


@pytest.mark.parametrize("delta", [-1, -10, -100_000])
def test_decrement_at_zero_changes_nothing_and_does_not_raise(delta):
    project = Project("Bufanda")
    project.change_rows(delta)
    project.change_knots(delta)
    assert (project.rows_done, project.knots_done) == (0, 0)


def test_high_counters_are_kept_whole():
    project = Project("Bufanda", rows_done=100_000)
    assert project.rows_done == 100_000

    project.change_rows(1)
    assert project.rows_done == 100_001

    project.change_rows(-1)
    assert project.rows_done == 100_000

    project.change_knots(100_000)
    assert project.knots_done == 100_000
