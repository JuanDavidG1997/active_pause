"""Config TOML loader and writer."""
from __future__ import annotations

import os
import tomllib
from pathlib import Path

import tomli_w

from active_pauses.config.defaults import DEFAULT_CONFIG_TOML
from active_pauses.config.schema import Config


def get_config_path() -> Path:
    """Return the path to config.toml, following XDG spec."""
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return config_home / "active-pauses" / "config.toml"


def load_config(path: Path | None = None) -> Config:
    """Load config from TOML file. Creates default config if file doesn't exist."""
    if path is None:
        path = get_config_path()

    if not path.exists():
        write_default_config(path)

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    return Config.model_validate(raw)


def write_default_config(path: Path) -> None:
    """Write the default config.toml to the given path, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_CONFIG_TOML, encoding="utf-8")


def write_config(config: Config, path: Path | None = None) -> None:
    """Serialize a Config to TOML and write it."""
    if path is None:
        path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(config.model_dump(), f)
