"""APScheduler-based per-muscle-group timer manager."""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore[import-untyped]

from active_pauses.config.schema import Config, MuscleGroupTimerConfig

logger = logging.getLogger(__name__)


class MuscleGroupScheduler:
    """Manages per-muscle-group APScheduler jobs."""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler()
        self._jobs: dict[str, str] = {}  # muscle_group -> job_id
        self._config: Config | None = None

    def configure(self, config: Config, callback: Callable[[str], None]) -> None:
        """Configure jobs from config. callback(muscle_group) fires on each tick."""
        self._config = config
        self._callback = callback

    def start(self) -> None:
        """Start the scheduler and all configured jobs."""
        assert self._config is not None, "Call configure() before start()"
        for group, timer_cfg in self._config.timers.items():
            if timer_cfg.enabled:
                self._add_job(group, timer_cfg)
        self._scheduler.start()
        logger.info("Scheduler started with %d jobs", len(self._jobs))

    def _add_job(self, group: str, timer_cfg: MuscleGroupTimerConfig) -> None:
        """Add an interval job for the given muscle group."""
        job = self._scheduler.add_job(
            self._callback,
            trigger=IntervalTrigger(minutes=timer_cfg.interval_minutes),
            args=[group],
            id=f"muscle_{group}",
            replace_existing=True,
        )
        self._jobs[group] = job.id
        logger.debug("Scheduled job for '%s' every %dm", group, timer_cfg.interval_minutes)

    def snooze(self, minutes: int) -> None:
        """Shift next_run_time for all active jobs by +minutes."""
        delta = timedelta(minutes=minutes)
        for job_id in self._jobs.values():
            job = self._scheduler.get_job(job_id)
            if job is not None and job.next_run_time is not None:
                new_time = job.next_run_time + delta
                job.modify(next_run_time=new_time)
        logger.info("Snoozed all jobs by %d minutes", minutes)

    def skip_current(self, group: str | None = None) -> None:
        """Reset next_run_time for job(s) to now + interval (skip current pending)."""
        assert self._config is not None
        groups = [group] if group else list(self._jobs.keys())
        for g in groups:
            job_id = self._jobs.get(g)
            if job_id is None:
                continue
            job = self._scheduler.get_job(job_id)
            if job is None:
                continue
            timer_cfg = self._config.timers.get(g)
            if timer_cfg is None:
                continue
            new_time = datetime.now(tz=UTC) + timedelta(
                minutes=timer_cfg.interval_minutes
            )
            job.modify(next_run_time=new_time)
        logger.info("Skipped current exercise for groups: %s", groups)

    def pause(self) -> None:
        """Pause all jobs."""
        self._scheduler.pause()
        logger.info("Scheduler paused")

    def resume(self) -> None:
        """Resume all jobs."""
        self._scheduler.resume()
        logger.info("Scheduler resumed")

    def get_next_run_times(self) -> dict[str, str | None]:
        """Return {group: iso8601_next_run} for all jobs."""
        result: dict[str, str | None] = {}
        for group, job_id in self._jobs.items():
            job = self._scheduler.get_job(job_id)
            if job is not None and job.next_run_time is not None:
                result[group] = job.next_run_time.isoformat()
            else:
                result[group] = None
        return result

    def shutdown(self) -> None:
        """Shutdown the scheduler cleanly."""
        self._scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")

    @property
    def running(self) -> bool:
        return bool(self._scheduler.running)

    @property
    def paused(self) -> bool:
        return bool(self._scheduler.state == 2)  # STATE_PAUSED
