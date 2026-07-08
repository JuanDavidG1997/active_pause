"""asyncio event loop entry point; wires all subsystems."""
from __future__ import annotations

import asyncio
import logging
import signal
from pathlib import Path

from active_pauses.config.loader import load_config
from active_pauses.config.schema import Config
from active_pauses.daemon.config_watcher import ConfigWatcher
from active_pauses.daemon.scheduler import MuscleGroupScheduler
from active_pauses.db.engine import get_engine, get_session_factory
from active_pauses.db.repositories.session_repo import SessionRepo
from active_pauses.exercises.loader import load_exercise_pack
from active_pauses.exercises.models import MuscleGroup
from active_pauses.exercises.registry import get_registry
from active_pauses.exercises.selector import ExerciseSelector

logger = logging.getLogger(__name__)


class Daemon:
    """The active-pauses background daemon."""

    def __init__(
        self,
        config_path: Path | None = None,
        db_url: str | None = None,
        exercises_dir: Path | None = None,
        simulate: bool = False,
    ) -> None:
        self._config_path = config_path
        self._db_url = db_url
        self._exercises_dir = exercises_dir
        self._simulate = simulate

        self._config: Config | None = None
        self._scheduler = MuscleGroupScheduler()
        self._selector = ExerciseSelector()
        self._session_id: int | None = None
        self._running = False
        self._paused = False
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Initialize and start all subsystems."""
        logger.info("active-pauses daemon starting")

        # Load config
        self._config = load_config(self._config_path)

        # Setup DB
        engine = get_engine(self._db_url)
        session_factory = get_session_factory(engine)

        with session_factory() as db_session:
            repo = SessionRepo(db_session)
            ws = repo.start_session()
            self._session_id = ws.id

        # Load exercises
        registry = get_registry()
        if self._exercises_dir and self._exercises_dir.exists():
            exercises = load_exercise_pack(self._exercises_dir)
            registry.register(exercises)
            logger.info("Loaded %d exercises", len(registry))

        # Configure and start scheduler
        self._scheduler.configure(self._config, self._on_exercise_due)
        self._scheduler.start()

        # Start config watcher
        if self._config_path is None:
            from active_pauses.config.loader import get_config_path
            effective_path = get_config_path()
        else:
            effective_path = self._config_path

        if effective_path.exists():
            self._watcher = ConfigWatcher(effective_path, self._on_config_changed)
            self._watcher.start()

        self._running = True
        logger.info("Daemon started (session_id=%d)", self._session_id)

    def _on_exercise_due(self, muscle_group: str) -> None:
        """Called by scheduler when an exercise is due."""
        assert self._config is not None
        if self._paused:
            return

        # Check active hours (compare HH:MM locally)
        import time as _time
        local = _time.localtime()
        start_h, start_m = (int(x) for x in self._config.active_hours.start.split(":"))
        end_h, end_m = (int(x) for x in self._config.active_hours.end.split(":"))
        current_minutes = local.tm_hour * 60 + local.tm_min
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        if not (start_minutes <= current_minutes < end_minutes):
            logger.debug("Outside active hours — skipping exercise for '%s'", muscle_group)
            return

        try:
            group = MuscleGroup(muscle_group)
        except ValueError:
            logger.error("Unknown muscle group: %s", muscle_group)
            return

        registry = get_registry()
        exercise = self._selector.select(
            registry.all(),
            group,
            contraindications=[],  # Phase 1: no profile yet
            intensity_cap=2,
        )

        if exercise is None:
            logger.warning("No exercise available for group '%s'", muscle_group)
            return

        if not self._simulate:
            from active_pauses.daemon.notification import send_exercise_notification
            send_exercise_notification(exercise, self._scheduler)
        else:
            logger.info("[SIMULATE] Exercise due: %s (%s)", exercise.name, muscle_group)

    def _on_config_changed(self) -> None:
        """Called when config.toml changes on disk."""
        logger.info("Reloading config...")
        try:
            self._config = load_config(self._config_path)
            logger.info("Config reloaded successfully")
        except Exception as e:
            logger.error("Config reload failed: %s", e)

    async def run(self) -> None:
        """Run until SIGTERM or stop() is called."""
        await self.start()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, self._handle_sigterm)
        loop.add_signal_handler(signal.SIGINT, self._handle_sigterm)

        logger.info("Daemon running, waiting for shutdown signal")
        await self._stop_event.wait()
        await self.stop()

    def _handle_sigterm(self) -> None:
        logger.info("Received shutdown signal")
        self._stop_event.set()

    async def stop(self) -> None:
        """Clean shutdown."""
        logger.info("Daemon shutting down...")
        self._running = False

        self._scheduler.shutdown()

        if hasattr(self, "_watcher"):
            self._watcher.stop()

        # Close work session
        if self._session_id is not None:
            engine = get_engine(self._db_url)
            session_factory = get_session_factory(engine)
            with session_factory() as db_session:
                repo = SessionRepo(db_session)
                repo.end_session(self._session_id)

        logger.info("Daemon stopped")

    def get_status(self) -> dict[str, object]:
        """Return current daemon status as a dict."""
        return {
            "running": self._running,
            "paused": self._paused,
            "session_id": self._session_id,
            "next_pause_times": self._scheduler.get_next_run_times(),
            "completed_today": 0,  # Phase 1 stub
        }


def run_daemon(
    config_path: Path | None = None,
    db_url: str | None = None,
    exercises_dir: Path | None = None,
) -> None:
    """Entry point for the daemon process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    daemon = Daemon(config_path=config_path, db_url=db_url, exercises_dir=exercises_dir)
    asyncio.run(daemon.run())
