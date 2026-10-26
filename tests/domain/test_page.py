from crochet_tracker.domain.project import Project


def test_page_starts_at_one():
    assert Project("Bufanda").guide_page == 1


def test_page_never_goes_below_one():
    project = Project("Bufanda")
    project.change_page(-1, total_pages=10)
    assert project.guide_page == 1
    project.change_page(-100)
    assert project.guide_page == 1


def test_page_moves_forward_and_back():
    project = Project("Bufanda")
    project.change_page(1, total_pages=10)
    assert project.guide_page == 2
    project.change_page(-1, total_pages=10)
    assert project.guide_page == 1


def test_page_stops_at_the_last_known_page():
    project = Project("Bufanda", guide_page=10)
    project.change_page(1, total_pages=10)
    assert project.guide_page == 10


def test_page_is_not_clamped_without_known_total():
    project = Project("Bufanda", guide_page=50)
    project.change_page(1)
    assert project.guide_page == 51


def test_restored_page_is_never_below_one():
    assert Project("Bufanda", guide_page=0).guide_page == 1
