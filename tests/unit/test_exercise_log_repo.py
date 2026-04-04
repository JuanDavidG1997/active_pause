"""Tests for ExerciseLogRepo with in-memory SQLite."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from active_pauses import __version__
from active_pauses.db.models import Base, ExerciseLog, MuscleGroupEnum, WorkSession
from active_pauses.db.repositories.exercise_log_repo import ExerciseLogRepo


@pytest.fixture()
def db_session():  # type: ignore[no-untyped-def]
    """Provide an in-memory SQLite session with fresh schema."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()

    # Create a work session
    ws = WorkSession(started_at=__import__("datetime").datetime.now(), daemon_version=__version__)
    session.add(ws)
    session.commit()

    yield session, ws.id
    session.close()
    engine.dispose()


def test_log_scheduled_creates_entry(db_session: tuple) -> None:
    """log_scheduled creates a row with outcome='scheduled'."""
    session, session_id = db_session
    repo = ExerciseLogRepo(session)
    entry = repo.log_scheduled(
        session_id=session_id,
        exercise_id="back_cat_cow",
        exercise_name="Cat-Cow Stretch",
        muscle_group=MuscleGroupEnum.BACK,
        intensity=1,
    )
    assert entry.id is not None
    assert entry.outcome == "scheduled"
    assert entry.session_id == session_id


def test_log_completed_updates_outcome(db_session: tuple) -> None:
    """log_completed changes outcome to 'completed' and sets timestamps."""
    session, session_id = db_session
    repo = ExerciseLogRepo(session)
    entry = repo.log_scheduled(
        session_id=session_id,
        exercise_id="back_cat_cow",
        exercise_name="Cat-Cow Stretch",
        muscle_group=MuscleGroupEnum.BACK,
        intensity=1,
    )
    repo.log_completed(entry.id, actual_duration_seconds=60)
    updated = session.get(ExerciseLog, entry.id)
    assert updated is not None
    assert updated.outcome == "completed"
    assert updated.completed_at is not None
    assert updated.actual_duration_seconds == 60


def test_log_skipped_updates_outcome(db_session: tuple) -> None:
    """log_skipped changes outcome to 'skipped'."""
    session, session_id = db_session
    repo = ExerciseLogRepo(session)
    entry = repo.log_scheduled(
        session_id=session_id,
        exercise_id="neck_0",
        exercise_name="Neck Tilt",
        muscle_group=MuscleGroupEnum.NECK,
        intensity=1,
    )
    repo.log_skipped(entry.id)
    updated = session.get(ExerciseLog, entry.id)
    assert updated is not None
    assert updated.outcome == "skipped"


def test_log_snoozed_updates_outcome(db_session: tuple) -> None:
    """log_snoozed changes outcome to 'snoozed'."""
    session, session_id = db_session
    repo = ExerciseLogRepo(session)
    entry = repo.log_scheduled(
        session_id=session_id,
        exercise_id="wrist_0",
        exercise_name="Wrist Circle",
        muscle_group=MuscleGroupEnum.WRISTS,
        intensity=1,
    )
    repo.log_snoozed(entry.id)
    updated = session.get(ExerciseLog, entry.id)
    assert updated is not None
    assert updated.outcome == "snoozed"


def test_get_completed_today_count(db_session: tuple) -> None:
    """get_completed_today_count returns correct count of completed exercises."""
    session, session_id = db_session
    repo = ExerciseLogRepo(session)

    # Log 3 exercises, complete 2
    for i in range(3):
        entry = repo.log_scheduled(
            session_id=session_id,
            exercise_id=f"back_{i}",
            exercise_name=f"Exercise {i}",
            muscle_group=MuscleGroupEnum.BACK,
            intensity=1,
        )
        if i < 2:
            repo.log_completed(entry.id)

    count = repo.get_completed_today_count(session_id)
    assert count == 2


def test_log_nonexistent_id_does_not_raise(db_session: tuple) -> None:
    """Updating a nonexistent log_id logs a warning but doesn't raise."""
    session, _ = db_session
    repo = ExerciseLogRepo(session)
    repo.log_completed(99999)  # Should not raise
    repo.log_skipped(99999)
    repo.log_snoozed(99999)
