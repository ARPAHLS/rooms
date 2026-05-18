import os

import cli


def test_set_session_env_key_tracks_new_keys():
    tracked = []
    key = "ROOMS_TEST_WIZARD_KEY"
    os.environ.pop(key, None)

    cli._set_session_env_key(tracked, key, "secret-value")

    assert tracked == [key]
    assert os.environ[key] == "secret-value"

    cli._cleanup_session_env(tracked)
    assert key not in os.environ


def test_set_session_env_key_skips_existing_keys():
    tracked = []
    key = "ROOMS_TEST_EXISTING_KEY"
    os.environ[key] = "pre-existing"

    cli._set_session_env_key(tracked, key, "new-value")

    assert tracked == []
    assert os.environ[key] == "pre-existing"

    os.environ.pop(key, None)


def test_cleanup_session_env_removes_only_tracked_keys():
    wizard_key = "ROOMS_TEST_CLEANUP_WIZARD"
    existing_key = "ROOMS_TEST_CLEANUP_EXISTING"
    os.environ.pop(wizard_key, None)
    os.environ[existing_key] = "keep-me"

    tracked = []
    cli._set_session_env_key(tracked, wizard_key, "wizard-secret")
    cli._cleanup_session_env(tracked)

    assert wizard_key not in os.environ
    assert os.environ[existing_key] == "keep-me"

    os.environ.pop(existing_key, None)
