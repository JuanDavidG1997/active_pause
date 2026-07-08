"""Tests for config loader, writer, and schema validation."""
from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from active_pauses.config.defaults import DEFAULT_CONFIG_TOML
from active_pauses.config.loader import load_config, write_config, write_default_config
from active_pauses.config.schema import Config


def test_load_default_config(tmp_path: Path) -> None:
    """load_config with nonexistent path creates file with defaults and returns Config."""
    config_path = tmp_path / "config.toml"
    assert not config_path.exists()

    config = load_config(config_path)

    assert config_path.exists(), "Default config file should be created"
    assert isinstance(config, Config)
    assert config.active_hours.start == "09:00"
    assert config.active_hours.end == "18:00"
    assert config.notification.snooze_minutes == 5
    assert config.notification.urgency == "normal"
    assert "back" in config.timers
    assert config.timers["eyes"].interval_minutes == 20


def test_load_existing_config(tmp_path: Path) -> None:
    """Write a custom config.toml to tmp_path, load it, assert values match."""
    config_path = tmp_path / "config.toml"
    custom_toml = """\
[active_hours]
start = "08:00"
end = "17:30"

[notification]
snooze_minutes = 10
urgency = "low"

[timers.back]
enabled = false
interval_minutes = 60

[timers.eyes]
enabled = true
interval_minutes = 15
"""
    config_path.write_text(custom_toml, encoding="utf-8")

    config = load_config(config_path)

    assert config.active_hours.start == "08:00"
    assert config.active_hours.end == "17:30"
    assert config.notification.snooze_minutes == 10
    assert config.notification.urgency == "low"
    assert config.timers["back"].enabled is False
    assert config.timers["back"].interval_minutes == 60
    assert config.timers["eyes"].interval_minutes == 15


def test_write_default_config(tmp_path: Path) -> None:
    """write_default_config creates file, file is valid TOML, parses to Config."""
    config_path = tmp_path / "subdir" / "config.toml"
    assert not config_path.exists()

    write_default_config(config_path)

    assert config_path.exists(), "Config file should be created"
    content = config_path.read_text(encoding="utf-8")
    assert content == DEFAULT_CONFIG_TOML

    # Ensure it's valid TOML
    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    # Ensure it parses to a Config
    config = Config.model_validate(raw)
    assert isinstance(config, Config)


def test_config_roundtrip(tmp_path: Path) -> None:
    """write_config then load_config returns same values (TOML roundtrip)."""
    config_path = tmp_path / "config.toml"

    original = Config()
    original.active_hours.start = "07:00"
    original.notification.urgency = "critical"
    original.notification.snooze_minutes = 15

    write_config(original, config_path)
    loaded = load_config(config_path)

    assert loaded.active_hours.start == "07:00"
    assert loaded.notification.urgency == "critical"
    assert loaded.notification.snooze_minutes == 15
    assert loaded.active_hours.end == original.active_hours.end


def test_active_hours_validation() -> None:
    """Invalid time format raises ValidationError."""
    with pytest.raises(ValidationError):
        Config.model_validate({"active_hours": {"start": "25:00", "end": "18:00"}})

    with pytest.raises(ValidationError):
        Config.model_validate({"active_hours": {"start": "not-a-time", "end": "18:00"}})

    with pytest.raises(ValidationError):
        Config.model_validate({"active_hours": {"start": "09:60", "end": "18:00"}})


def test_interval_validation() -> None:
    """interval_minutes < 1 raises ValidationError."""
    with pytest.raises(ValidationError):
        Config.model_validate({"timers": {"back": {"interval_minutes": 0}}})

    with pytest.raises(ValidationError):
        Config.model_validate({"timers": {"back": {"interval_minutes": 481}}})


def test_urgency_validation() -> None:
    """Invalid urgency raises ValidationError."""
    with pytest.raises(ValidationError):
        Config.model_validate({"notification": {"urgency": "extreme"}})
