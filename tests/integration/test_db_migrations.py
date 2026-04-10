"""Integration tests for Alembic database migrations."""
from __future__ import annotations

from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config

EXPECTED_TABLES = {
    "user_profile",
    "work_sessions",
    "exercise_log",
    "posture_events",
    "daily_stats",
    "streak",
    "badges",
    "calendar_accounts",
    "installed_packs",
}


def make_alembic_config(db_url: str, worktree_root: Path) -> Config:
    """Build an Alembic Config pointing at a temporary DB."""
    alembic_ini = worktree_root / "alembic.ini"
    cfg = Config(str(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


def get_existing_tables(db_url: str) -> set[str]:
    """Return the set of user-created table names in the DB."""
    engine = sa.create_engine(db_url)
    with engine.connect() as conn:
        inspector = sa.inspect(conn)
        tables = set(inspector.get_table_names())
    engine.dispose()
    # Exclude Alembic's own version table
    tables.discard("alembic_version")
    return tables


@pytest.fixture()
def worktree_root() -> Path:
    """Absolute path to the worktree root (where alembic.ini lives)."""
    return Path(__file__).parent.parent.parent


@pytest.fixture()
def db_url(tmp_path: Path) -> str:
    """Return a SQLite DB URL backed by a temp file."""
    db_file = tmp_path / "test_active_pauses.db"
    return f"sqlite:///{db_file}"


def test_upgrade_creates_all_tables(db_url: str, worktree_root: Path) -> None:
    """alembic upgrade head creates all 9 expected tables."""
    cfg = make_alembic_config(db_url, worktree_root)
    command.upgrade(cfg, "head")
    tables = get_existing_tables(db_url)
    assert tables == EXPECTED_TABLES, (
        f"Missing: {EXPECTED_TABLES - tables}, Extra: {tables - EXPECTED_TABLES}"
    )


def test_downgrade_drops_all_tables(db_url: str, worktree_root: Path) -> None:
    """alembic downgrade base drops all tables."""
    cfg = make_alembic_config(db_url, worktree_root)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    tables = get_existing_tables(db_url)
    assert tables == set(), f"Tables still present after downgrade: {tables}"


def test_upgrade_head_idempotency(db_url: str, worktree_root: Path) -> None:
    """upgrade -> downgrade -> upgrade again succeeds (idempotency)."""
    cfg = make_alembic_config(db_url, worktree_root)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    tables = get_existing_tables(db_url)
    assert tables == EXPECTED_TABLES, (
        f"Missing after re-upgrade: {EXPECTED_TABLES - tables}"
    )
