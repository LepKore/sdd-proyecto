import sqlite3
from dataclasses import replace

import pytest

from crochet_tracker.domain.project import Project
from crochet_tracker.infrastructure.sqlite_repository import SqliteProjectRepository

T0 = 1_761_400_000


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "crochet.db"


@pytest.fixture
def repository(db_path):
    return SqliteProjectRepository(db_path)


def add(repository, name, now=T0):
    project_id = repository.add(Project(name), now)
    return repository.get(project_id)


def test_creating_a_project_stores_it(repository):
    project = Project("Bufanda de lana")
    project_id = repository.add(project, T0)

    stored = repository.get(project_id)

    assert stored is not None
    assert stored.id == project_id
    assert stored.name == "Bufanda de lana"
    assert (stored.rows_done, stored.knots_done) == (0, 0)
    assert stored.is_finished is False
    assert stored.guide_page == 1
    assert stored.guide_file is None
    assert stored.created_at == T0
    assert stored.updated_at == T0


def test_created_projects_persist_across_repositories(db_path, repository):
    project_id = repository.add(Project("Bufanda"), T0)

    assert SqliteProjectRepository(db_path).get(project_id).name == "Bufanda"


def test_the_list_is_ordered_by_last_modification(repository):
    add(repository, "vieja", now=T0)
    add(repository, "media", now=T0 + 10)
    add(repository, "nueva", now=T0 + 20)

    assert [project.name for project in repository.list_all()] == ["nueva", "media", "vieja"]


def test_projects_with_the_same_timestamp_are_ordered_by_id_desc(repository):
    first = repository.add(Project("primera"), T0)
    second = repository.add(Project("segunda"), T0)

    assert [project.id for project in repository.list_all()] == [second, first]


def test_opening_a_project_does_not_reorder_the_list(repository):
    old = add(repository, "vieja", now=T0)
    add(repository, "nueva", now=T0 + 20)

    reopened = repository.get(old.id)

    assert reopened.updated_at == T0
    assert [project.name for project in repository.list_all()] == ["nueva", "vieja"]


def test_an_unknown_project_is_none(repository):
    assert repository.get(999) is None


def test_the_list_is_empty_without_projects(repository):
    assert repository.list_all() == []


def test_foreign_keys_are_enforced(db_path, repository):
    repository.add(Project("Bufanda"), T0)

    with pytest.raises(sqlite3.IntegrityError):
        with sqlite3.connect(db_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "INSERT INTO note (project_id, body, created_at) VALUES (999, 'suelta', 0)"
            )


def save_and_reload(db_path, repository, project, now):
    repository.save(project, now)
    return SqliteProjectRepository(db_path).get(project.id)


def test_renaming_persists_and_bumps_updated_at(db_path, repository):
    project = add(repository, "Bufanda", now=T0)
    project.name = "Bufanda larga"

    reloaded = save_and_reload(db_path, repository, project, T0 + 30)

    assert reloaded.name == "Bufanda larga"
    assert reloaded.updated_at == T0 + 30


def test_finishing_a_project_persists_both_ways(db_path, repository):
    project = add(repository, "Bufanda")

    project.toggle_finished()
    assert save_and_reload(db_path, repository, project, T0 + 1).is_finished is True

    project.toggle_finished()
    assert save_and_reload(db_path, repository, project, T0 + 2).is_finished is False


def test_counter_changes_persist_and_do_not_touch_the_other_counter(db_path, repository):
    project = add(repository, "Bufanda")

    project.change_rows(1)
    reloaded = save_and_reload(db_path, repository, project, T0 + 1)
    assert (reloaded.rows_done, reloaded.knots_done) == (1, 0)

    project.change_knots(1)
    reloaded = save_and_reload(db_path, repository, project, T0 + 2)
    assert (reloaded.rows_done, reloaded.knots_done) == (1, 1)


def test_the_guide_page_persists(db_path, repository):
    project = add(repository, "Bufanda")
    project.change_page(1, total_pages=10)

    reloaded = save_and_reload(db_path, repository, project, T0 + 1)

    assert reloaded.guide_page == project.guide_page == 2


def test_every_change_reads_back_the_same_after_reopening(db_path, repository):
    project = add(repository, "Bufanda", now=T0)
    project.name = "Bufanda larga"
    project.change_rows(2)
    project.change_knots(3)
    project.toggle_finished()
    project.change_page(1, total_pages=10)

    reloaded = save_and_reload(db_path, repository, project, T0 + 1)

    assert reloaded == replace(project, updated_at=T0 + 1)

