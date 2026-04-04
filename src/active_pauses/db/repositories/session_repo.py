"""CRUD for work_sessions table."""
from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from active_pauses import __version__
from active_pauses.db.models import WorkSession

logger = logging.getLogger(__name__)


class SessionRepo:
    """Repository for work session operations."""

    def __init__(self, db_session: Session) -> None:
        self._session = db_session

    def start_session(self) -> WorkSession:
        """Create and persist a new work session."""
        ws = WorkSession(
            started_at=datetime.now(tz=UTC),
            daemon_version=__version__,
        )
        self._session.add(ws)
        self._session.commit()
        logger.info("Work session %d started", ws.id)
        return ws

    def end_session(self, session_id: int) -> None:
        """Mark a work session as ended."""
        ws = self._session.get(WorkSession, session_id)
        if ws is None:
            logger.warning("WorkSession %d not found", session_id)
            return
        ws.ended_at = datetime.now(tz=UTC)
        self._session.commit()
        logger.info("Work session %d ended", session_id)
