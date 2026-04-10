"""CRUD for exercise_log table."""
from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from active_pauses.db.models import ExerciseLog, MuscleGroupEnum

logger = logging.getLogger(__name__)


class ExerciseLogRepo:
    """Repository for exercise log operations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def log_scheduled(
        self,
        session_id: int,
        exercise_id: str,
        exercise_name: str,
        muscle_group: MuscleGroupEnum,
        intensity: int,
        pack_id: str = "builtin",
    ) -> ExerciseLog:
        """Record that an exercise was scheduled/prompted."""
        entry = ExerciseLog(
            session_id=session_id,
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            muscle_group=muscle_group,
            pack_id=pack_id,
            intensity=intensity,
            outcome="scheduled",
            scheduled_at=datetime.now(tz=UTC),
        )
        self._session.add(entry)
        self._session.commit()
        return entry

    def log_completed(self, log_id: int, actual_duration_seconds: int | None = None) -> None:
        """Mark an exercise log entry as completed."""
        entry = self._session.get(ExerciseLog, log_id)
        if entry is None:
            logger.warning("ExerciseLog %d not found", log_id)
            return
        now = datetime.now(tz=UTC)
        entry.outcome = "completed"
        entry.completed_at = now
        if entry.started_at is None:
            entry.started_at = now
        if actual_duration_seconds is not None:
            entry.actual_duration_seconds = actual_duration_seconds
        self._session.commit()

    def log_skipped(self, log_id: int) -> None:
        """Mark an exercise log entry as skipped."""
        entry = self._session.get(ExerciseLog, log_id)
        if entry is None:
            logger.warning("ExerciseLog %d not found", log_id)
            return
        entry.outcome = "skipped"
        self._session.commit()

    def log_snoozed(self, log_id: int) -> None:
        """Mark an exercise log entry as snoozed."""
        entry = self._session.get(ExerciseLog, log_id)
        if entry is None:
            logger.warning("ExerciseLog %d not found", log_id)
            return
        entry.outcome = "snoozed"
        self._session.commit()

    def get_completed_today_count(self, session_id: int) -> int:
        """Return the count of completed exercises in the current session."""
        from sqlalchemy import func, select

        stmt = (
            select(func.count())
            .where(ExerciseLog.session_id == session_id)
            .where(ExerciseLog.outcome == "completed")
        )
        return self._session.execute(stmt).scalar_one()
