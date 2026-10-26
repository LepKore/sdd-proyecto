"""Open a project with its saved progress (RF-3, RF-17)."""

from crochet_tracker.application.ports import ProjectRepository
from crochet_tracker.domain.project import Project


def open_project(repository: ProjectRepository, project_id: int) -> Project | None:
    """Return the saved state of the project, or None if it was deleted meanwhile (CL-7).

    Reading does not touch updated_at, so opening does not reorder the list (RF-2).
    """
    return repository.get(project_id)
