"""Errors the application raises and the view turns into a message (RF-13)."""


class SaveFailed(Exception):
    """The change was not written; the caller must show the previous value (RF-13)."""


class GuideError(Exception):
    """The guide could not be copied or read; the project stays as it was (RF-8)."""
