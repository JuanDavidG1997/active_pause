"""Initial schema - all 9 tables.

Revision ID: 0001
Revises:
Create Date: 2026-04-03 00:00:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # user_profile
    op.create_table(
        "user_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "profile_type",
            sa.Enum(
                "desk_worker",
                "programmer",
                "senior",
                "postpartum",
                "gamer",
                name="profiletypeenum",
            ),
            nullable=False,
        ),
        sa.Column("intensity_cap", sa.Integer(), nullable=False),
        sa.Column("contraindications", sa.Text(), nullable=False),
        sa.Column("gender_expr", sa.String(length=10), nullable=False),
        sa.Column("skin_tone", sa.String(length=4), nullable=False),
        sa.Column("face_variant", sa.String(length=4), nullable=False),
        sa.Column("clothing_style", sa.String(length=32), nullable=False),
        sa.Column("reduced_motion", sa.Boolean(), nullable=False),
        sa.Column("audio_cues", sa.Boolean(), nullable=False),
        sa.Column("audio_volume", sa.Integer(), nullable=False),
        sa.Column("screen_reader_mode", sa.Boolean(), nullable=False),
        sa.Column("font_size", sa.String(length=16), nullable=False),
        sa.Column("high_contrast", sa.Boolean(), nullable=False),
        sa.Column("onboarding_complete", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_profile_id", "user_profile", ["id"], unique=True)

    # work_sessions
    op.create_table(
        "work_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("daemon_version", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_sessions_started_at", "work_sessions", ["started_at"])

    # exercise_log
    op.create_table(
        "exercise_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.String(length=64), nullable=False),
        sa.Column("exercise_name", sa.String(length=128), nullable=False),
        sa.Column(
            "muscle_group",
            sa.Enum(
                "back",
                "neck",
                "wrists",
                "eyes",
                "legs",
                "fullbody",
                "shoulders",
                "hips",
                name="musclegroupenum",
            ),
            nullable=False,
        ),
        sa.Column("pack_id", sa.String(length=64), nullable=False),
        sa.Column("intensity", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(length=16), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("actual_duration_seconds", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["work_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercise_log_session_id", "exercise_log", ["session_id"])
    op.create_index("ix_exercise_log_scheduled_at", "exercise_log", ["scheduled_at"])
    op.create_index("ix_exercise_log_muscle_group", "exercise_log", ["muscle_group"])
    op.create_index("ix_exercise_log_outcome", "exercise_log", ["outcome"])

    # posture_events
    op.create_table(
        "posture_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column(
            "state",
            sa.Enum("sitting", "standing", name="posturestateenum"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["work_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_posture_events_started_at", "posture_events", ["started_at"])
    op.create_index("ix_posture_events_state", "posture_events", ["state"])

    # daily_stats
    op.create_table(
        "daily_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stat_date", sa.Date(), nullable=False),
        sa.Column("exercises_completed", sa.Integer(), nullable=False),
        sa.Column("exercises_skipped", sa.Integer(), nullable=False),
        sa.Column("exercises_snoozed", sa.Integer(), nullable=False),
        sa.Column("body_score", sa.Float(), nullable=True),
        sa.Column("standing_minutes", sa.Float(), nullable=False),
        sa.Column("sitting_minutes", sa.Float(), nullable=False),
        sa.Column("muscle_group_counts", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stat_date"),
    )
    op.create_index("ix_daily_stats_stat_date", "daily_stats", ["stat_date"])

    # streak
    op.create_table(
        "streak",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("streak_days", sa.Integer(), nullable=False),
        sa.Column("longest_streak", sa.Integer(), nullable=False),
        sa.Column("last_active_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # badges
    op.create_table(
        "badges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("badge_id", sa.String(length=64), nullable=False),
        sa.Column("earned_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("badge_id", name="uq_badges_badge_id"),
    )

    # calendar_accounts
    op.create_table(
        "calendar_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("cal_type", sa.String(length=16), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("identifier", sa.String(length=256), nullable=False),
        sa.Column("suppress_during_events", sa.Boolean(), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.Column("secret_key", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id"),
    )

    # installed_packs
    op.create_table(
        "installed_packs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pack_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("author", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("license", sa.String(length=64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("builtin", sa.Boolean(), nullable=False),
        sa.Column("installed_at", sa.DateTime(), nullable=False),
        sa.Column("pack_path", sa.String(length=512), nullable=False),
        sa.Column("exercise_count", sa.Integer(), nullable=False),
        sa.Column("valid", sa.Boolean(), nullable=False),
        sa.Column("validation_error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pack_id"),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("installed_packs")
    op.drop_table("calendar_accounts")
    op.drop_table("badges")
    op.drop_table("streak")
    op.drop_table("daily_stats")
    op.drop_table("posture_events")
    op.drop_table("exercise_log")
    op.drop_table("work_sessions")
    op.drop_table("user_profile")
