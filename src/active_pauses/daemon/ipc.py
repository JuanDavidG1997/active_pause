"""DBus service org.activepause.Daemon (dasbus).

Phase 1: stub implementation that works without a running GTK main loop.
The full dasbus service registration requires a running D-Bus session bus,
so in Phase 1 we provide the interface definition and a mock-friendly wrapper.
"""
from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

DBUS_SERVICE_NAME = "org.activepause.Daemon"
DBUS_OBJECT_PATH = "/org/activepause/Daemon"


class DaemonInterface:
    """DBus interface for the active-pauses daemon.

    Implements the 6 required methods:
    - Pause()
    - Resume()
    - SnoozeMinutes(n: int)
    - GetStatus() -> str  (JSON)
    - TriggerExercise(exercise_id: str)
    - Quit()
    """

    def __init__(self, daemon: object) -> None:
        """Bind to a Daemon instance for state access."""
        self._daemon = daemon

    def Pause(self) -> None:  # noqa: N802
        """Pause all exercise timers."""
        logger.info("DBus: Pause()")
        from active_pauses.daemon.main import Daemon
        if isinstance(self._daemon, Daemon):
            self._daemon._scheduler.pause()
            self._daemon._paused = True

    def Resume(self) -> None:  # noqa: N802
        """Resume all exercise timers."""
        logger.info("DBus: Resume()")
        from active_pauses.daemon.main import Daemon
        if isinstance(self._daemon, Daemon):
            self._daemon._scheduler.resume()
            self._daemon._paused = False

    def SnoozeMinutes(self, n: int) -> None:  # noqa: N802
        """Snooze all timers by n minutes."""
        logger.info("DBus: SnoozeMinutes(%d)", n)
        from active_pauses.daemon.main import Daemon
        if isinstance(self._daemon, Daemon):
            self._daemon._scheduler.snooze(n)

    def GetStatus(self) -> str:  # noqa: N802
        """Return JSON status string."""
        logger.info("DBus: GetStatus()")
        from active_pauses.daemon.main import Daemon
        if isinstance(self._daemon, Daemon):
            status = self._daemon.get_status()
            return json.dumps(status)
        return json.dumps({"running": False, "paused": False})

    def TriggerExercise(self, exercise_id: str) -> None:  # noqa: N802
        """Immediately trigger an exercise by ID."""
        logger.info("DBus: TriggerExercise(%s)", exercise_id)
        from active_pauses.exercises.registry import get_registry
        registry = get_registry()
        exercise = registry.get(exercise_id)
        if exercise is None:
            logger.error("Exercise '%s' not found", exercise_id)
            return
        logger.info("[Phase 1 stub] Would show exercise window for: %s", exercise.name)

    def Quit(self) -> None:  # noqa: N802
        """Request daemon shutdown."""
        logger.info("DBus: Quit()")
        from active_pauses.daemon.main import Daemon
        if isinstance(self._daemon, Daemon):
            self._daemon._stop_event.set()
