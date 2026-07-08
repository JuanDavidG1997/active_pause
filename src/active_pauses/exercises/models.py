from __future__ import annotations

import re
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, field_validator


class MuscleGroup(StrEnum):
    BACK = "back"
    NECK = "neck"
    WRISTS = "wrists"
    EYES = "eyes"
    LEGS = "legs"
    FULLBODY = "fullbody"
    SHOULDERS = "shoulders"
    HIPS = "hips"


class ExercisePhase(BaseModel):
    name: Literal["inhale", "exhale", "hold", "move", "rest"]
    duration_seconds: int  # 1-60
    cue: str  # <=120 chars

    @field_validator("duration_seconds")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if not 1 <= v <= 60:
            raise ValueError(f"duration_seconds must be 1-60, got {v}")
        return v

    @field_validator("cue")
    @classmethod
    def validate_cue(cls, v: str) -> str:
        if len(v) > 120:
            raise ValueError(f"cue must be <=120 chars, got {len(v)}")
        return v


class Exercise(BaseModel):
    # Required fields
    id: str
    name: str
    muscle_groups: list[MuscleGroup]
    intensity: int  # 1, 2, or 3
    duration_seconds: int  # 10-300
    rest_seconds: int  # 0-60
    animation_ref: str
    research_source: str
    verbal_cue: str  # <=120 chars
    phases: list[ExercisePhase]

    # Optional fields
    hold_seconds: int | None = None
    reps: int | None = None
    sets: int | None = None
    contraindications: list[str] = []
    bilateral: bool = False
    equipment: list[str] = []
    notes: str | None = None
    tags: list[str] = []

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9_]+$", v):
            raise ValueError(f"id must match [a-z0-9_]+, got '{v}'")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) > 60:
            raise ValueError(f"name must be <=60 chars, got {len(v)}")
        return v

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v: int) -> int:
        if v not in (1, 2, 3):
            raise ValueError(f"intensity must be 1, 2, or 3, got {v}")
        return v

    @field_validator("duration_seconds")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if not 10 <= v <= 300:
            raise ValueError(f"duration_seconds must be 10-300, got {v}")
        return v

    @field_validator("rest_seconds")
    @classmethod
    def validate_rest(cls, v: int) -> int:
        if not 0 <= v <= 60:
            raise ValueError(f"rest_seconds must be 0-60, got {v}")
        return v

    @field_validator("verbal_cue")
    @classmethod
    def validate_verbal_cue(cls, v: str) -> str:
        if len(v) > 120:
            raise ValueError(f"verbal_cue must be <=120 chars, got {len(v)}")
        return v

    @field_validator("muscle_groups")
    @classmethod
    def validate_muscle_groups(cls, v: list[MuscleGroup]) -> list[MuscleGroup]:
        if len(v) < 1:
            raise ValueError("muscle_groups must have >=1 entry")
        return v

    @field_validator("phases")
    @classmethod
    def validate_phases(cls, v: list[ExercisePhase]) -> list[ExercisePhase]:
        if len(v) < 1:
            raise ValueError("phases must have >=1 entry")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError(f"notes must be <=500 chars, got {len(v)}")
        return v
