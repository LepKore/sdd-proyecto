import inspect

import pytest

from crochet_tracker.domain import errors
from crochet_tracker.domain.errors import DomainError, EmptyNoteText, InvalidProjectName

ALL_ERRORS = [DomainError, InvalidProjectName, EmptyNoteText]


@pytest.mark.parametrize("error", ALL_ERRORS)
def test_errors_are_domain_errors(error):
    assert issubclass(error, DomainError)
    assert issubclass(error, Exception)


@pytest.mark.parametrize("error", ALL_ERRORS[1:])
def test_errors_are_catchable_as_domain_error(error):
    with pytest.raises(DomainError):
        raise error("message")


def test_error_messages_are_english_only():
    source = inspect.getsource(errors)
    assert source.isascii(), "domain errors must not contain user-facing Spanish text"
