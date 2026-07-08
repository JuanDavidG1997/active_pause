"""Selects an exercise based on profile, contraindications, and recency."""
from __future__ import annotations

import logging
import random
from collections import deque

from active_pauses.exercises.models import Exercise, MuscleGroup

logger = logging.getLogger(__name__)

RECENCY_WINDOW = 3  # Avoid repeating the last N exercises per group


class ExerciseSelector:
    """Selects exercises respecting profile constraints and recency."""

    def __init__(self) -> None:
        # Per-group recent exercise IDs (avoid repetition)
        self._recent: dict[str, deque[str]] = {}

    def select(
        self,
        exercises: list[Exercise],
        group: MuscleGroup,
        contraindications: list[str],
        intensity_cap: int,
    ) -> Exercise | None:
        """Select one exercise for the given muscle group.

        Filters by:
        - muscle_group membership
        - contraindications overlap
        - intensity_cap
        - recency (deprioritize last RECENCY_WINDOW exercises)

        Returns None if no eligible exercises exist (logs warning).
        """
        candidates = [
            ex for ex in exercises
            if group in ex.muscle_groups
            and ex.intensity <= intensity_cap
            and not set(ex.contraindications) & set(contraindications)
        ]

        if not candidates:
            logger.warning(
                "No eligible exercises for group '%s' with contraindications=%s, cap=%d",
                group,
                contraindications,
                intensity_cap,
            )
            return None

        recent_ids = self._recent.get(group.value, deque())

        # Separate candidates into non-recent and recent
        non_recent = [ex for ex in candidates if ex.id not in recent_ids]
        pool = non_recent if non_recent else candidates  # Fall back if all are recent

        chosen = random.choice(pool)

        # Update recency window
        if group.value not in self._recent:
            self._recent[group.value] = deque(maxlen=RECENCY_WINDOW)
        self._recent[group.value].append(chosen.id)

        return chosen
