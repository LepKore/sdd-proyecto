import pytest

from crochet_tracker.domain.note import Note
from crochet_tracker.domain.project import Project
from crochet_tracker.infrastructure.sqlite_repository import SqliteProjectRepository

T0 = 1_761_400_000


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "crochet.db"


@pytest.fixture
def repository(db_path):
    return SqliteProjectRepository(db_path)


@pytest.fixture
def guides_dir(tmp_path):
    directory = tmp_path / "guides"
    directory.mkdir()
    return directory


def test_deleting_a_project_removes_it_from_the_list(repository):
    keep = repository.add(Project("se queda"), T0)
    gone = repository.add(Project("se va"), T0 + 10)

    repository.delete_project(gone)

    assert repository.get(gone) is None
    assert [project.id for project in repository.list_all()] == [keep]


def test_deleting_a_project_removes_its_notes(repository):
    project_id = repository.add(Project("con notas"), T0)
    repository.add_note(project_id, Note("una nota", T0))

    repository.delete_project(project_id)

    assert repository.list_notes(project_id) == []


def test_deleting_a_project_removes_its_copied_guide(repository, project_id_with_guide):
    project_id, guide = project_id_with_guide
    assert guide.is_file()

    repository.delete_project(project_id)

    assert not guide.exists()


def test_deleting_a_project_without_a_guide_keeps_the_other_guides(
    repository, guides_dir, tmp_path
):
    keep = repository.add(Project("con guía", guide_file="1-keep.pdf"), T0)
    gone = repository.add(Project("sin guía"), T0)
    other_guide = guides_dir / "1-keep.pdf"
    other_guide.write_bytes(b"%PDF-1.7")

    repository.delete_project(gone)

    assert repository.get(keep) is not None
    assert other_guide.is_file()


def test_deleting_a_missing_project_does_nothing(repository):
    project_id = repository.add(Project("existe"), T0)

    repository.delete_project(9999)

    assert repository.get(project_id) is not None


@pytest.fixture
def project_id_with_guide(repository, guides_dir):
    guide = guides_dir / "7-guide.pdf"
    guide.write_bytes(b"%PDF-1.7")
    project = Project("con guía", guide_file=guide.name)
    return repository.add(project, T0), guide
