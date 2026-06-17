import os

from rooms.env import bootstrap_environment, dotenv_search_paths


def test_dotenv_search_paths_prefers_cwd_before_repo_root(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    work = repo / "work"
    work.mkdir(parents=True)
    monkeypatch.chdir(work)
    monkeypatch.setattr("rooms.env.repo_root", lambda: repo)

    paths = dotenv_search_paths()
    assert paths[0] == (work / ".env").resolve()
    assert paths[1] == (repo / ".env").resolve()


def test_bootstrap_environment_loads_env_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("ROOMS_TEST_ENV_KEY=bootstrap-value\n", encoding="utf-8")
    os.environ.pop("ROOMS_TEST_ENV_KEY", None)

    loaded = bootstrap_environment(force=True)
    assert loaded == [(tmp_path / ".env").resolve()]
    assert os.environ["ROOMS_TEST_ENV_KEY"] == "bootstrap-value"

    os.environ.pop("ROOMS_TEST_ENV_KEY", None)


def test_bootstrap_environment_does_not_override_existing_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("ROOMS_TEST_ENV_KEY=from-dotenv\n", encoding="utf-8")
    os.environ["ROOMS_TEST_ENV_KEY"] = "from-shell"

    bootstrap_environment(force=True)
    assert os.environ["ROOMS_TEST_ENV_KEY"] == "from-shell"

    os.environ.pop("ROOMS_TEST_ENV_KEY", None)


def test_load_settings_bootstraps_env(tmp_path, monkeypatch):
    import rooms.env as env_module

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("ROOMS_TEST_SETTINGS_ENV=loaded\n", encoding="utf-8")
    os.environ.pop("ROOMS_TEST_SETTINGS_ENV", None)
    env_module._BOOTSTRAPPED = False

    from rooms.settings import load_settings

    load_settings()
    assert os.environ["ROOMS_TEST_SETTINGS_ENV"] == "loaded"

    os.environ.pop("ROOMS_TEST_SETTINGS_ENV", None)
