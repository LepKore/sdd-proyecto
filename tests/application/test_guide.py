"""Guide and page use cases (RF-8, RF-9, RF-10, T24)."""

import pytest

from crochet_tracker.application.attach_guide import attach_guide
from crochet_tracker.application.change_page import change_page
from crochet_tracker.application.create_project import create_project
from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.open_project import open_project
from tests.application.fakes import FakeClock, FakeGuideStore, FakeRepository


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def guides() -> FakeGuideStore:
    return FakeGuideStore()


@pytest.fixture
def project(repository, clock):
    return create_project(repository, clock, "Bufanda")


@pytest.fixture
def pdf(tmp_path):
    source = tmp_path / "guia.pdf"
    source.write_bytes(b"%PDF-1.4 guia")
    return source


def test_attaching_a_guide_copies_it_and_remembers_its_name(
    repository, clock, project, guides, pdf
):
    assert attach_guide(repository, clock, project, guides, pdf) is True
    assert project.guide_file in guides.files
    assert open_project(repository, project.id).guide_file == project.guide_file


def test_a_project_with_a_guide_gets_no_second_one(repository, clock, project, guides, pdf):
    attach_guide(repository, clock, project, guides, pdf)
    name = project.guide_file
    other = pdf.with_name("otra.pdf")
    other.write_bytes(b"%PDF-1.4 otra")
    assert attach_guide(repository, clock, project, guides, other) is False
    assert project.guide_file == name
    assert len(guides.files) == 1


def test_an_unreadable_file_leaves_the_project_without_a_guide(
    repository, clock, project, guides, tmp_path
):
    with pytest.raises(OSError):
        attach_guide(repository, clock, project, guides, tmp_path / "no-existe.pdf")
    assert project.guide_file is None
    assert guides.files == {}


def test_a_guide_that_cannot_be_saved_is_not_assigned(repository, clock, project, guides, pdf):
    repository.fail_on_write = True
    with pytest.raises(SaveFailed):
        attach_guide(repository, clock, project, guides, pdf)
    assert project.guide_file is None
    assert open_project(repository, project.id).guide_file is None


def test_the_new_page_is_saved_at_once(repository, clock, project):
    change_page(repository, clock, project, 1)
    assert project.guide_page == 2
    assert open_project(repository, project.id).guide_page == 2


def test_the_first_page_cannot_go_back(repository, clock, project):
    change_page(repository, clock, project, -1)
    assert project.guide_page == 1
    assert repository.saves == 0


def test_the_last_page_cannot_go_forward(repository, clock, project):
    change_page(repository, clock, project, 1, total_pages=2)
    change_page(repository, clock, project, 1, total_pages=2)
    assert project.guide_page == 2
    assert open_project(repository, project.id).guide_page == 2


def test_a_page_that_cannot_be_saved_goes_back(repository, clock, project):
    repository.fail_on_write = True
    with pytest.raises(SaveFailed):
        change_page(repository, clock, project, 1)
    assert project.guide_page == 1
