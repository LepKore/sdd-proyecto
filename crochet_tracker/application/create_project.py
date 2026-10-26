"""Create a project with an empty progress (RF-1)."""

from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.project import Project


def create_project(repository: ProjectRepository, clock: Clock, name: str) -> Project:
    """Add the project and return it with its id and timestamps.

    The name is validated by the domain: an empty or blank one raises
    InvalidProjectName and nothing is stored (CL-1, CL-2).
    """
    project = Project(name=name)
    now = clock.now()
    project.created_at = now
    project.updated_at = now
    project.id = repository.add(project, now)
    return project
