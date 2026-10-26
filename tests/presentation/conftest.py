import pytest

from crochet_tracker.presentation.main_window import MainWindow
from tests.application.fakes import FakeClock, FakeGuideStore, FakeRepository


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def guides(tmp_path) -> FakeGuideStore:
    return FakeGuideStore(tmp_path / "guides")


@pytest.fixture
def window(qtbot, repository, clock, guides) -> MainWindow:
    window = MainWindow(repository, clock, guides)
    qtbot.addWidget(window)
    return window
