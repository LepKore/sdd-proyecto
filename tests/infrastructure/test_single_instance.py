"""One lock per data folder: the first process wins (RF-7, CL-29, T32)."""

from crochet_tracker.infrastructure.single_instance import SingleInstance


def test_first_process_gets_the_lock(tmp_path) -> None:
    assert SingleInstance(tmp_path).acquire() is True


def test_second_process_is_refused(tmp_path) -> None:
    first = SingleInstance(tmp_path)
    first.acquire()

    assert SingleInstance(tmp_path).acquire() is False


def test_releasing_allows_starting_again(tmp_path) -> None:
    first = SingleInstance(tmp_path)
    first.acquire()
    first.release()

    assert SingleInstance(tmp_path).acquire() is True


def test_the_lock_lives_in_the_data_folder(tmp_path) -> None:
    instance = SingleInstance(tmp_path)
    instance.acquire()

    assert (tmp_path / "app.lock").exists()
    instance.release()


def test_two_data_folders_do_not_block_each_other(tmp_path) -> None:
    uno = tmp_path / "uno"
    otro = tmp_path / "otro"
    uno.mkdir()
    otro.mkdir()

    assert SingleInstance(uno).acquire() is True
    assert SingleInstance(otro).acquire() is True
