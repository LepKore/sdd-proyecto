"""Attach a guide to a project that has none (RF-8, RF-9)."""

from pathlib import Path

from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, GuideStore, ProjectRepository
from crochet_tracker.domain.project import Project


def attach_guide(
    repository: ProjectRepository,
    clock: Clock,
    project: Project,
    guides: GuideStore,
    source: Path,
) -> bool:
    """Copy the PDF into the project data and remember its name; False if it already has one.

    A file that cannot be read raises the store's GuideError and leaves the project as it
    was: there is never a second guide and never a half-copied one (CL-10, CL-11).
    """
    if project.guide_file:
        return False
    name = guides.copy(project.id, source)
    project.guide_file = name
    try:
        repository.save(project, clock.now())
    except Exception as error:
        project.guide_file = None
        raise SaveFailed("No se pudo guardar la guía") from error
    return True
