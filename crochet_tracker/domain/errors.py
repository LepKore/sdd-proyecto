"""Domain exceptions.

Messages here are developer-facing and written in English (constitution, section 6).
User-facing text belongs to the presentation layer.
"""


class DomainError(Exception):
    """Base class for every rule violation raised by the domain."""


class InvalidProjectName(DomainError):
    """Raised when a project name is empty, blank or longer than 100 characters."""


class EmptyNoteText(DomainError):
    """Raised when a note text is empty or contains only whitespace."""
