"""Loads and validates TOML exercise packs."""
from __future__ import annotations

import tomllib
from pathlib import Path

from active_pauses.exercises.models import Exercise
from active_pauses.exercises.schema import check_forbidden_keys


class ExerciseLoadError(ValueError):
    """Raised when an exercise file fails to load or validate."""

    pass


def load_exercise_file(path: Path) -> list[Exercise]:
    """Load and validate all exercises from a TOML file.

    Raises ExerciseLoadError if validation fails.
    Raises ForbiddenKeyError (subclass of ValueError) if forbidden keys found.
    """
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ExerciseLoadError(f"Failed to read {path}: {e}") from e

    # Security: reject forbidden keys before any processing
    check_forbidden_keys(data)

    exercises_data = data.get("exercise", [])
    if not isinstance(exercises_data, list):
        raise ExerciseLoadError(f"Expected 'exercise' to be a list in {path}")

    exercises: list[Exercise] = []
    for i, raw in enumerate(exercises_data):
        try:
            exercises.append(Exercise.model_validate(raw))
        except Exception as e:
            exercise_id = raw.get("id", f"index {i}") if isinstance(raw, dict) else f"index {i}"
            raise ExerciseLoadError(
                f"Exercise '{exercise_id}' in {path} failed validation: {e}"
            ) from e

    return exercises


def load_exercise_pack(pack_dir: Path) -> list[Exercise]:
    """Load all exercise TOML files from a pack directory."""
    all_exercises: list[Exercise] = []
    for toml_file in sorted(pack_dir.glob("*.toml")):
        all_exercises.extend(load_exercise_file(toml_file))
    return all_exercises
