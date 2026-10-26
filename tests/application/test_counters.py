"""Counter use cases and their immediate save (RF-11, RF-12, RF-13, T21)."""

import pytest

from crochet_tracker.application.counters import add_knots, add_rows, remove_knots, remove_rows
from crochet_tracker.application.create_project import create_project
from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.open_project import open_project
from tests.application.fakes import FakeClock, FakeRepository


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def project(repository, clock):
    return create_project(repository, clock, "Bufanda")


def test_rows_counter_is_independent(repository, clock, project):
    add_rows(repository, clock, project)
    assert (project.rows_done, project.knots_done) == (1, 0)


def test_knots_counter_is_independent(repository, clock, project):
    add_knots(repository, clock, project)
    assert (project.rows_done, project.knots_done) == (0, 1)


def test_every_count_is_saved_at_once(repository, clock, project):
    add_rows(repository, clock, project)
    add_knots(repository, clock, project)
    add_knots(repository, clock, project)
    reopened = open_project(repository, project.id)
    assert (reopened.rows_done, reopened.knots_done) == (1, 2)


def test_remove_takes_one_off_a_positive_counter(repository, clock, project):
    add_rows(repository, clock, project)
    add_rows(repository, clock, project)
    remove_rows(repository, clock, project)
    assert project.rows_done == 1
    assert open_project(repository, project.id).rows_done == 1


def test_remove_knots_takes_one_off_a_positive_counter(repository, clock, project):
    add_knots(repository, clock, project)
    remove_knots(repository, clock, project)
    assert project.knots_done == 0
    assert open_project(repository, project.id).knots_done == 0


@pytest.mark.parametrize("remove", [remove_rows, remove_knots])
def test_removing_at_zero_changes_and_saves_nothing(repository, clock, project, remove):
    remove(repository, clock, project)
    assert (project.rows_done, project.knots_done) == (0, 0)
    assert repository.saves == 0


def test_counters_have_no_ceiling(repository, clock, project):
    project.rows_done = 100_000
    add_rows(repository, clock, project)
    assert open_project(repository, project.id).rows_done == 100_001


def test_counting_on_a_finished_project_keeps_it_finished(repository, clock, project):
    project.is_finished = True
    repository.save(project, clock.now())
    add_rows(repository, clock, project)
    assert open_project(repository, project.id).is_finished is True


@pytest.mark.parametrize(
    "counting", [add_rows, add_knots, remove_rows, remove_knots]
)
def test_a_failed_save_puts_the_counter_back(repository, clock, project, counting):
    project.rows_done = 5
    project.knots_done = 5
    repository.save(project, clock.now())
    repository.fail_on_save = True

    with pytest.raises(SaveFailed) as failure:
        counting(repository, clock, project)

    assert str(failure.value)
    assert (project.rows_done, project.knots_done) == (5, 5)
    assert open_project(repository, project.id).rows_done == 5
