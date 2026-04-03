from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all active-pauses models."""


class MuscleGroupEnum(StrEnum):
    BACK = "back"
    NECK = "neck"
    WRISTS = "wrists"
    EYES = "eyes"
    LEGS = "legs"
    FULLBODY = "fullbody"
    SHOULDERS = "shoulders"
    HIPS = "hips"


class ProfileTypeEnum(StrEnum):
    DESK_WORKER = "desk_worker"
    PROGRAMMER = "programmer"
    SENIOR = "senior"
    POSTPARTUM = "postpartum"
    GAMER = "gamer"


class PostureStateEnum(StrEnum):
    SITTING = "sitting"
    STANDING = "standing"


class UserProfile(Base):
    """Single-row table representing the user's health profile and preferences."""

    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    profile_type: Mapped[ProfileTypeEnum] = mapped_column(
        Enum(ProfileTypeEnum), nullable=False, default=ProfileTypeEnum.DESK_WORKER
    )
    intensity_cap: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    contraindications: Mapped[str] = mapped_column(Text, nullable=False, default="")
    gender_expr: Mapped[str] = mapped_column(String(10), nullable=False, default="masc")
    skin_tone: Mapped[str] = mapped_column(String(4), nullable=False, default="s1")
    face_variant: Mapped[str] = mapped_column(String(4), nullable=False, default="a")
    clothing_style: Mapped[str] = mapped_column(
        String(32), nullable=False, default="casual_default"
    )
    reduced_motion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    audio_cues: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    audio_volume: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    screen_reader_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    font_size: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    high_contrast: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_user_profile_id", "id", unique=True),)


class WorkSession(Base):
    """Represents one continuous working session (daemon uptime block)."""

    __tablename__ = "work_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    daemon_version: Mapped[str] = mapped_column(String(32), nullable=False)

    exercise_logs: Mapped[list[ExerciseLog]] = relationship(back_populates="session")
    posture_events: Mapped[list[PostureEvent]] = relationship(back_populates="session")

    __table_args__ = (Index("ix_work_sessions_started_at", "started_at"),)


class ExerciseLog(Base):
    """Records each time an exercise was presented and the outcome."""

    __tablename__ = "exercise_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("work_sessions.id"), nullable=False)
    exercise_id: Mapped[str] = mapped_column(String(64), nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(128), nullable=False)
    muscle_group: Mapped[MuscleGroupEnum] = mapped_column(
        Enum(MuscleGroupEnum), nullable=False
    )
    pack_id: Mapped[str] = mapped_column(String(64), nullable=False, default="builtin")
    intensity: Mapped[int] = mapped_column(Integer, nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session: Mapped[WorkSession] = relationship(back_populates="exercise_logs")

    __table_args__ = (
        Index("ix_exercise_log_session_id", "session_id"),
        Index("ix_exercise_log_scheduled_at", "scheduled_at"),
        Index("ix_exercise_log_muscle_group", "muscle_group"),
        Index("ix_exercise_log_outcome", "outcome"),
    )


class PostureEvent(Base):
    """Records transitions between sitting and standing states."""

    __tablename__ = "posture_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("work_sessions.id"), nullable=False)
    state: Mapped[PostureStateEnum] = mapped_column(Enum(PostureStateEnum), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)

    session: Mapped[WorkSession] = relationship(back_populates="posture_events")

    __table_args__ = (
        Index("ix_posture_events_started_at", "started_at"),
        Index("ix_posture_events_state", "state"),
    )


class DailyStats(Base):
    """Materialized daily aggregate."""

    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    exercises_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exercises_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exercises_snoozed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    body_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    standing_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sitting_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    muscle_group_counts: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    __table_args__ = (Index("ix_daily_stats_stat_date", "stat_date"),)


class Streak(Base):
    """Current and historical streak data. Single-row (id=1)."""

    __tablename__ = "streak"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )


class Badge(Base):
    """Earned badges."""

    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    badge_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    __table_args__ = (UniqueConstraint("badge_id", name="uq_badges_badge_id"),)


class CalendarAccount(Base):
    """Connected calendar account."""

    __tablename__ = "calendar_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    cal_type: Mapped[str] = mapped_column(String(16), nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    identifier: Mapped[str] = mapped_column(String(256), nullable=False)
    suppress_during_events: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    secret_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )


class InstalledPack(Base):
    """Tracks installed exercise packs."""

    __tablename__ = "installed_packs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pack_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    author: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    license: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    installed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    pack_path: Mapped[str] = mapped_column(String(512), nullable=False)
    exercise_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    validation_error: Mapped[str | None] = mapped_column(Text, nullable=True)
