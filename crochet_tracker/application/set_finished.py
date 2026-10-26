"""Mark a project as finished or back in progress (RF-5)."""

from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.project import Project


def set_finished(repository: ProjectRepository, clock: Clock, project: Project) -> None:
    """Swap the finished state and store it at once (RF-5, RF-13)."""
    previous = project.is_finished
    project.toggle_finished()
    try:
        repository.save(project, clock.now())
    except Exception as error:
        project.is_finished = previous
        raise SaveFailed("No se pudo guardar el estado del proyecto") from error
