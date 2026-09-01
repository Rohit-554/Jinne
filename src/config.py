import os
from pathlib import Path

from dotenv import load_dotenv


def load_config(env_path: str | Path | None = None) -> None:
    load_dotenv(dotenv_path=env_path, override=False)


def get_env(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
