"""List the projects, newest change first (RF-2)."""

from crochet_tracker.application.ports import ProjectRepository
from crochet_tracker.domain.project import Project


def list_projects(repository: ProjectRepository) -> list[Project]:
    """Return every saved project; opening one does not move it in the list (RF-2)."""
    return repository.list_all()
