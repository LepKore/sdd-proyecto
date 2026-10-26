from crochet_tracker.infrastructure.app_paths import APP_DIR_NAME, DATA_ENV_VAR, data_dir


def test_override_wins_and_is_created(monkeypatch, tmp_path):
    target = tmp_path / "nested" / "datos"
    monkeypatch.setenv(DATA_ENV_VAR, str(target))

    assert data_dir() == target
    assert target.is_dir()


def test_override_is_used_even_when_it_already_exists(monkeypatch, tmp_path):
    target = tmp_path / "datos"
    target.mkdir()
    monkeypatch.setenv(DATA_ENV_VAR, str(target))

    assert data_dir() == target


def test_without_override_the_user_folder_is_used(monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.delenv(DATA_ENV_VAR, raising=False)

    result = data_dir()

    assert result == tmp_path / APP_DIR_NAME
    assert result.is_dir()


def test_without_appdata_it_falls_back_to_the_home_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.delenv(DATA_ENV_VAR, raising=False)
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))

    result = data_dir()

    assert result == tmp_path / ".local" / "share" / APP_DIR_NAME
    assert result.is_dir()


def test_calling_twice_is_harmless(monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.delenv(DATA_ENV_VAR, raising=False)

    assert data_dir() == data_dir()
