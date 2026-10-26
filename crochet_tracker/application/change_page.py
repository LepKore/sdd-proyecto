"""Move through the guide and remember the page (RF-10, RF-13)."""

from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.project import Project


def change_page(
    repository: ProjectRepository,
    clock: Clock,
    project: Project,
    delta: int,
    total_pages: int | None = None,
) -> None:
    """Go forward or back one page and store it at once, or stay put at the edges (RF-10).

    total_pages keeps the remembered page inside the document when the count is known.
    """
    previous = project.guide_page
    project.change_page(delta, total_pages)
    if project.guide_page == previous:
        return
    try:
        repository.save(project, clock.now())
    except Exception as error:
        project.guide_page = previous
        raise SaveFailed("No se pudo guardar la página") from error
