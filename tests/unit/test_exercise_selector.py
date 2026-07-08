"""Tests for ExerciseSelector."""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from active_pauses.exercises.models import Exercise, ExercisePhase, MuscleGroup
from active_pauses.exercises.selector import RECENCY_WINDOW, ExerciseSelector


def make_exercise(
    id: str,
    groups: list[str],
    intensity: int = 1,
    contraindications: list[str] | None = None,
) -> Exercise:
    return Exercise(
        id=id,
        name=id.replace("_", " ").title(),
        muscle_groups=[MuscleGroup(g) for g in groups],
        intensity=intensity,
        duration_seconds=30,
        rest_seconds=5,
        animation_ref=id,
        research_source="test",
        verbal_cue="Test cue",
        phases=[ExercisePhase(name="hold", duration_seconds=5, cue="Hold")],
        contraindications=contraindications or [],
    )


BACK_EXERCISES = [make_exercise(f"back_{i}", ["back"]) for i in range(5)]
NECK_EXERCISES = [make_exercise(f"neck_{i}", ["neck"]) for i in range(3)]


def test_select_returns_exercise_for_group() -> None:
    """Selector returns an exercise matching the requested group."""
    selector = ExerciseSelector()
    result = selector.select(BACK_EXERCISES, MuscleGroup.BACK, [], 3)
    assert result is not None
    assert MuscleGroup.BACK in result.muscle_groups


def test_select_wrong_group_returns_none() -> None:
    """Selector returns None when no exercises match the group."""
    selector = ExerciseSelector()
    result = selector.select(BACK_EXERCISES, MuscleGroup.EYES, [], 3)
    assert result is None


def test_contraindication_filters_exercise() -> None:
    """Exercises with matching contraindications are excluded."""
    exercises = [
        make_exercise("back_safe", ["back"]),
        make_exercise("back_risky", ["back"], contraindications=["spinal_surgery"]),
    ]
    selector = ExerciseSelector()
    for _ in range(20):
        result = selector.select(exercises, MuscleGroup.BACK, ["spinal_surgery"], 3)
        assert result is not None
        assert result.id == "back_safe"


def test_intensity_cap_filters_exercise() -> None:
    """Exercises above intensity cap are excluded."""
    exercises = [
        make_exercise("back_gentle", ["back"], intensity=1),
        make_exercise("back_vigorous", ["back"], intensity=3),
    ]
    selector = ExerciseSelector()
    for _ in range(20):
        result = selector.select(exercises, MuscleGroup.BACK, [], intensity_cap=2)
        assert result is not None
        assert result.id == "back_gentle"


def test_all_filtered_returns_none(caplog: pytest.LogCaptureFixture) -> None:
    """Returns None and logs a warning if all exercises are filtered out."""
    import logging

    exercises = [make_exercise("back_bad", ["back"], contraindications=["spinal_surgery"])]
    selector = ExerciseSelector()
    with caplog.at_level(logging.WARNING):
        result = selector.select(exercises, MuscleGroup.BACK, ["spinal_surgery"], 3)
    assert result is None
    assert any("No eligible exercises" in r.message for r in caplog.records)


def test_recency_avoids_repetition() -> None:
    """Selector avoids last RECENCY_WINDOW exercises when alternatives exist."""
    exercises = [make_exercise(f"back_{i}", ["back"]) for i in range(10)]
    selector = ExerciseSelector()

    chosen = []
    for _ in range(RECENCY_WINDOW + 3):
        ex = selector.select(exercises, MuscleGroup.BACK, [], 3)
        assert ex is not None
        chosen.append(ex.id)

    # Within the last RECENCY_WINDOW choices, no exercise should repeat
    # (given we have 10 exercises >> RECENCY_WINDOW)
    recent = chosen[-RECENCY_WINDOW:]
    assert len(set(recent)) == RECENCY_WINDOW, f"Repetition in recent window: {recent}"


def test_recency_falls_back_when_all_recent() -> None:
    """Selector falls back to all candidates if all are in recent window."""
    # Only 2 exercises, recency window is 3 — must still return something
    exercises = [make_exercise(f"back_{i}", ["back"]) for i in range(2)]
    selector = ExerciseSelector()
    for _ in range(10):
        result = selector.select(exercises, MuscleGroup.BACK, [], 3)
        assert result is not None


def test_independent_recency_per_group() -> None:
    """Recency tracking is independent per muscle group."""
    exercises = [
        make_exercise("back_0", ["back"]),
        make_exercise("neck_0", ["neck"]),
    ]
    selector = ExerciseSelector()
    b = selector.select(exercises, MuscleGroup.BACK, [], 3)
    n = selector.select(exercises, MuscleGroup.NECK, [], 3)
    assert b is not None and b.id == "back_0"
    assert n is not None and n.id == "neck_0"


@given(
    contraindications=st.lists(st.sampled_from(["spinal_surgery", "neck_surgery"]), max_size=2),
    intensity_cap=st.integers(min_value=1, max_value=3),
)
@settings(max_examples=30)
def test_hypothesis_selector_never_violates_constraints(
    contraindications: list[str], intensity_cap: int
) -> None:
    """Hypothesis: selector never returns an exercise violating constraints."""
    exercises = [
        make_exercise("back_0", ["back"], intensity=1, contraindications=["spinal_surgery"]),
        make_exercise("back_1", ["back"], intensity=2),
        make_exercise("back_2", ["back"], intensity=3),
    ]
    selector = ExerciseSelector()
    result = selector.select(exercises, MuscleGroup.BACK, contraindications, intensity_cap)
    if result is not None:
        assert result.intensity <= intensity_cap
        assert not set(result.contraindications) & set(contraindications)
