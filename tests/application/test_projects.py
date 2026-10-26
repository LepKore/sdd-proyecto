"""Project use cases, tested with in-memory doubles only (RF-1..RF-6, T20)."""

import pathlib

import pytest

from crochet_tracker.application.create_project import create_project
from crochet_tracker.application.delete_project import delete_project
from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.list_projects import list_projects
from crochet_tracker.application.open_project import open_project
from crochet_tracker.application.ports import Clock, GuideStore, ProjectRepository
from crochet_tracker.application.rename_project import rename_project
from crochet_tracker.application.set_finished import set_finished
from crochet_tracker.domain.errors import InvalidProjectName
from crochet_tracker.domain.note import Note
from tests.application.fakes import FakeClock, FakeGuideStore, FakeRepository

APPLICATION_DIR = (
    pathlib.Path(__file__).resolve().parents[2] / "crochet_tracker" / "application"
)


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


def test_created_project_starts_empty(repository, clock):
    project = create_project(repository, clock, "  Bufanda de lana  ")
    assert project.id is not None
    assert project.name == "Bufanda de lana"
    assert (project.rows_done, project.knots_done, project.is_finished) == (0, 0, False)
    assert project.created_at == project.updated_at == clock.now()
    assert open_project(repository, project.id).name == "Bufanda de lana"


@pytest.mark.parametrize("name", ["", "   ", "\n\t ", "x" * 101])
def test_create_rejects_names_the_domain_refuses(repository, clock, name):
    with pytest.raises(InvalidProjectName):
        create_project(repository, clock, name)
    assert list_projects(repository) == []


def test_duplicate_names_are_allowed(repository, clock):
    create_project(repository, clock, "Bufanda")
    create_project(repository, clock, "Bufanda")
    assert len(list_projects(repository)) == 2


def test_list_is_empty_at_start(repository):
    assert list_projects(repository) == []


def test_list_shows_the_most_recently_changed_first(repository, clock):
    first = create_project(repository, clock, "Bufanda")
    clock.advance(60)
    second = create_project(repository, clock, "Gorro")
    assert [p.id for p in list_projects(repository)] == [second.id, first.id]


def test_open_returns_the_saved_progress(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    project.rows_done = 12
    project.knots_done = 340
    repository.save(project, clock.now())
    reopened = open_project(repository, project.id)
    assert (reopened.rows_done, reopened.knots_done) == (12, 340)


def test_open_a_deleted_project_returns_none(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    delete_project(repository, project.id)
    assert open_project(repository, project.id) is None


def test_open_does_not_reorder_the_list(repository, clock):
    first = create_project(repository, clock, "Bufanda")
    clock.advance(60)
    create_project(repository, clock, "Gorro")
    open_project(repository, first.id)
    assert [p.name for p in list_projects(repository)] == ["Gorro", "Bufanda"]


def test_rename_is_saved_and_survives_reopening(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    rename_project(repository, clock, project, "  Chal  ")
    assert project.name == "Chal"
    assert open_project(repository, project.id).name == "Chal"


def test_rename_to_a_blank_name_keeps_the_previous_one(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    with pytest.raises(InvalidProjectName):
        rename_project(repository, clock, project, "   ")
    assert project.name == "Bufanda"
    assert open_project(repository, project.id).name == "Bufanda"


def test_rename_restores_the_old_name_when_saving_fails(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    repository.fail_on_save = True
    with pytest.raises(SaveFailed):
        rename_project(repository, clock, project, "Chal")
    assert project.name == "Bufanda"
    assert open_project(repository, project.id).name == "Bufanda"


def test_finished_state_toggles_and_is_saved(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    set_finished(repository, clock, project)
    assert project.is_finished is True
    assert open_project(repository, project.id).is_finished is True
    set_finished(repository, clock, project)
    assert project.is_finished is False
    assert open_project(repository, project.id).is_finished is False


def test_finished_state_is_kept_when_saving_fails(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    repository.fail_on_save = True
    with pytest.raises(SaveFailed):
        set_finished(repository, clock, project)
    assert project.is_finished is False
    assert open_project(repository, project.id).is_finished is False


def test_delete_removes_the_project_and_its_notes(repository, clock):
    project = create_project(repository, clock, "Bufanda")
    repository.add_note(project.id, Note("primera", clock.now()))
    delete_project(repository, project.id)
    assert open_project(repository, project.id) is None
    assert repository.list_notes(project.id) == []


def test_delete_of_a_missing_project_is_silent(repository):
    delete_project(repository, 404)


def test_fakes_implement_the_ports():
    assert isinstance(FakeRepository(), ProjectRepository)
    assert isinstance(FakeGuideStore(), GuideStore)
    assert isinstance(FakeClock(), Clock)


def test_application_does_not_import_outer_layers():
    forbidden = ("sqlite3", "PySide6", "pypdfium2", "crochet_tracker.infrastructure")
    for path in APPLICATION_DIR.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for module in forbidden:
            assert module not in source, f"{path.name} uses {module}"
