"""Singleton registry of all loaded exercises."""
from __future__ import annotations

from active_pauses.exercises.models import Exercise, MuscleGroup


class ExerciseRegistry:
    """Holds all loaded exercises, indexed by ID and muscle group."""

    def __init__(self) -> None:
        self._exercises: dict[str, Exercise] = {}

    def register(self, exercises: list[Exercise]) -> None:
        """Add exercises to the registry."""
        for ex in exercises:
            self._exercises[ex.id] = ex

    def get(self, exercise_id: str) -> Exercise | None:
        return self._exercises.get(exercise_id)

    def all(self) -> list[Exercise]:
        return list(self._exercises.values())

    def by_muscle_group(self, group: MuscleGroup) -> list[Exercise]:
        return [ex for ex in self._exercises.values() if group in ex.muscle_groups]

    def __len__(self) -> int:
        return len(self._exercises)


_registry: ExerciseRegistry | None = None


def get_registry() -> ExerciseRegistry:
    global _registry
    if _registry is None:
        _registry = ExerciseRegistry()
    return _registry
