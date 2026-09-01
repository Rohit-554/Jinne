import os

from src.config import get_env, load_config


def test_load_config_reads_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("COMPANION_TEST_VAR=hello-from-env\n")

    os.environ.pop("COMPANION_TEST_VAR", None)
    load_config(env_path=env_file)

    assert get_env("COMPANION_TEST_VAR") == "hello-from-env"

    os.environ.pop("COMPANION_TEST_VAR", None)


def test_get_env_required_raises_when_missing():
    os.environ.pop("COMPANION_MISSING_VAR", None)
    try:
        get_env("COMPANION_MISSING_VAR", required=True)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass
