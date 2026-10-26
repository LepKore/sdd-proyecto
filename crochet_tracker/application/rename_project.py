"""Rename an open project (RF-4)."""

from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.project import Project, normalize_name


def rename_project(
    repository: ProjectRepository, clock: Clock, project: Project, name: str
) -> None:
    """Store the new name, or keep the previous one and raise SaveFailed (RF-13).

    A blank name raises InvalidProjectName before anything is written (CL-1, CL-6).
    """
    new_name = normalize_name(name)
    previous = project.name
    project.name = new_name
    try:
        repository.save(project, clock.now())
    except Exception as error:
        project.name = previous
        raise SaveFailed("No se pudo guardar el nombre") from error
