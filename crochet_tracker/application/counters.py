"""Counters and their immediate save (RF-11, RF-12, RF-13)."""

from crochet_tracker.application.errors import SaveFailed
from crochet_tracker.application.ports import Clock, ProjectRepository
from crochet_tracker.domain.project import Project


def _save(
    repository: ProjectRepository, clock: Clock, project: Project, rows: int, knots: int
) -> None:
    """Store the counter change, or put both counters back and report (RF-13)."""
    try:
        repository.save(project, clock.now())
    except Exception as error:
        project.restore_rows(rows)
        project.restore_knots(knots)
        raise SaveFailed("No se pudo guardar el contador") from error


def add_rows(repository: ProjectRepository, clock: Clock, project: Project) -> None:
    """Count one more row; the knot counter is left as it was (RF-11)."""
    rows, knots = project.rows_done, project.knots_done
    project.change_rows(1)
    _save(repository, clock, project, rows, knots)


def remove_rows(repository: ProjectRepository, clock: Clock, project: Project) -> None:
    """Count one row less; at zero nothing changes and nothing is written (RF-12, CL-17)."""
    if project.rows_done == 0:
        return
    rows, knots = project.rows_done, project.knots_done
    project.change_rows(-1)
    _save(repository, clock, project, rows, knots)


def add_knots(repository: ProjectRepository, clock: Clock, project: Project) -> None:
    """Count one more knot; the row counter is left as it was (RF-11)."""
    rows, knots = project.rows_done, project.knots_done
    project.change_knots(1)
    _save(repository, clock, project, rows, knots)


def remove_knots(repository: ProjectRepository, clock: Clock, project: Project) -> None:
    """Count one knot less; at zero nothing changes and nothing is written (RF-12, CL-17)."""
    if project.knots_done == 0:
        return
    rows, knots = project.rows_done, project.knots_done
    project.change_knots(-1)
    _save(repository, clock, project, rows, knots)
