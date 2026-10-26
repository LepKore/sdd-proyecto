import pytest

from crochet_tracker.presentation.main_window import MainWindow
from tests.application.fakes import FakeClock, FakeRepository


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def window(qtbot, repository, clock) -> MainWindow:
    window = MainWindow(repository, clock)
    qtbot.addWidget(window)
    return window
