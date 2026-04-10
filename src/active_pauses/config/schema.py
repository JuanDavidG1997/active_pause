"""Pydantic models for config.toml structure."""
from __future__ import annotations

from pydantic import BaseModel, field_validator


class MuscleGroupTimerConfig(BaseModel):
    """Per-muscle-group timer configuration."""

    enabled: bool = True
    interval_minutes: int = 45  # How often to prompt for this group

    @field_validator("interval_minutes")
    @classmethod
    def validate_interval(cls, v: int) -> int:
        if not 1 <= v <= 480:
            raise ValueError(f"interval_minutes must be 1–480, got {v}")
        return v


class ActiveHoursConfig(BaseModel):
    """Active hours configuration (daemon only fires during these hours)."""

    start: str = "09:00"  # HH:MM format
    end: str = "18:00"  # HH:MM format

    @field_validator("start", "end")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError(f"Time must be HH:MM format, got '{v}'")
        try:
            hour, minute = int(parts[0]), int(parts[1])
        except ValueError:
            raise ValueError(f"Time must be HH:MM format, got '{v}'")
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Invalid time '{v}'")
        return v


class NotificationConfig(BaseModel):
    """Notification behavior configuration."""

    snooze_minutes: int = 5
    urgency: str = "normal"  # low, normal, critical

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        if v not in ("low", "normal", "critical"):
            raise ValueError(f"urgency must be low/normal/critical, got '{v}'")
        return v

    @field_validator("snooze_minutes")
    @classmethod
    def validate_snooze(cls, v: int) -> int:
        if not 1 <= v <= 60:
            raise ValueError(f"snooze_minutes must be 1–60, got {v}")
        return v


class Config(BaseModel):
    """Root configuration model for config.toml."""

    active_hours: ActiveHoursConfig = ActiveHoursConfig()
    notification: NotificationConfig = NotificationConfig()

    # Per-muscle-group timer configs — key is muscle group name
    timers: dict[str, MuscleGroupTimerConfig] = {
        "back": MuscleGroupTimerConfig(interval_minutes=45),
        "neck": MuscleGroupTimerConfig(interval_minutes=45),
        "wrists": MuscleGroupTimerConfig(interval_minutes=30),
        "eyes": MuscleGroupTimerConfig(interval_minutes=20),
        "legs": MuscleGroupTimerConfig(interval_minutes=60),
        "fullbody": MuscleGroupTimerConfig(interval_minutes=90),
    }
