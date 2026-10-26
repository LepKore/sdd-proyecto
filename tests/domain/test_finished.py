from crochet_tracker.domain.project import Project


def test_projects_start_unfinished():
    assert Project("Bufanda").is_finished is False


def test_toggle_switches_both_ways():
    project = Project("Bufanda")
    project.toggle_finished()
    assert project.is_finished is True
    project.toggle_finished()
    assert project.is_finished is False


def test_toggling_twice_returns_to_the_initial_state():
    for initial in (False, True):
        project = Project("Bufanda", is_finished=initial)
        project.toggle_finished()
        project.toggle_finished()
        assert project.is_finished is initial


def test_counting_on_a_finished_project_keeps_it_finished():
    project = Project("Bufanda", is_finished=True)
    project.change_rows(1)
    project.change_knots(1)
    project.change_rows(-1)
    assert project.is_finished is True


def test_counting_on_an_unfinished_project_keeps_it_unfinished():
    project = Project("Bufanda")
    project.change_rows(1)
    project.change_knots(1)
    assert project.is_finished is False
