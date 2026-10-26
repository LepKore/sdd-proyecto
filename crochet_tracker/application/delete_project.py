"""Delete a project with its progress, notes and copied guide (RF-6).

The confirmation, which must show the project name, belongs to the view.
"""

from crochet_tracker.application.ports import ProjectRepository


def delete_project(repository: ProjectRepository, project_id: int) -> None:
    """Remove the project and everything that belongs to it; nothing happens if it is gone."""
    repository.delete_project(project_id)
