"""Tests for MuscleGroupScheduler."""
from __future__ import annotations

from collections.abc import Generator

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from active_pauses.config.schema import Config, MuscleGroupTimerConfig
from active_pauses.daemon.scheduler import MuscleGroupScheduler


def make_config(**overrides: int) -> Config:
    """Build a minimal Config with customizable intervals."""
    timers = {
        "back": MuscleGroupTimerConfig(interval_minutes=overrides.get("back", 45)),
        "neck": MuscleGroupTimerConfig(interval_minutes=overrides.get("neck", 45)),
    }
    return Config(timers=timers)


@pytest.fixture()
def started_scheduler() -> Generator[MuscleGroupScheduler, None, None]:

    fired: list[str] = []
    scheduler = MuscleGroupScheduler()
    config = make_config(back=1, neck=2)
    scheduler.configure(config, lambda g: fired.append(g))
    scheduler.start()
    yield scheduler
    scheduler.shutdown()


def test_scheduler_starts_and_has_jobs(started_scheduler: MuscleGroupScheduler) -> None:
    """Scheduler starts with jobs for each enabled muscle group."""
    assert started_scheduler.running
    times = started_scheduler.get_next_run_times()
    assert "back" in times
    assert "neck" in times
    assert times["back"] is not None


def test_snooze_shifts_next_run_time(started_scheduler: MuscleGroupScheduler) -> None:
    """Snooze(N) shifts all next_run_times forward by N minutes."""
    from datetime import datetime

    before = {
        k: datetime.fromisoformat(v)
        for k, v in started_scheduler.get_next_run_times().items()
        if v
    }
    started_scheduler.snooze(10)
    after = {
        k: datetime.fromisoformat(v)
        for k, v in started_scheduler.get_next_run_times().items()
        if v
    }

    for group in before:
        delta = after[group] - before[group]
        # Allow ±2s tolerance for scheduler timing
        assert 598 <= delta.total_seconds() <= 602, (
            f"Group '{group}' snooze delta was {delta.total_seconds()}s"
        )


def test_pause_and_resume(started_scheduler: MuscleGroupScheduler) -> None:
    """Pause sets paused state; resume restores running state."""
    started_scheduler.pause()
    assert started_scheduler.paused
    started_scheduler.resume()
    assert not started_scheduler.paused


def test_shutdown_stops_scheduler() -> None:
    """Shutdown stops the scheduler."""
    scheduler = MuscleGroupScheduler()
    config = make_config()
    scheduler.configure(config, lambda g: None)
    scheduler.start()
    assert scheduler.running
    scheduler.shutdown()
    assert not scheduler.running


def test_skip_current_resets_timer(started_scheduler: MuscleGroupScheduler) -> None:
    """skip_current resets the next_run_time for the given group."""
    from datetime import datetime

    started_scheduler.snooze(60)  # Push into future
    before_back = datetime.fromisoformat(
        started_scheduler.get_next_run_times()["back"]  # type: ignore[arg-type]
    )

    started_scheduler.skip_current("back")

    after_back = datetime.fromisoformat(
        started_scheduler.get_next_run_times()["back"]  # type: ignore[arg-type]
    )
    # After skip, next run should be ~interval from now (sooner than snoozed time)
    assert after_back < before_back


@given(snooze_minutes=st.integers(min_value=1, max_value=120))
@settings(max_examples=20)
def test_snooze_hypothesis(snooze_minutes: int) -> None:
    """Hypothesis: snooze always shifts time forward for valid minute values."""
    from datetime import datetime

    scheduler = MuscleGroupScheduler()
    config = make_config(back=45)
    scheduler.configure(config, lambda g: None)
    scheduler.start()
    try:
        before = datetime.fromisoformat(
            scheduler.get_next_run_times().get("back", "")  # type: ignore[arg-type]
        )
        scheduler.snooze(snooze_minutes)
        after = datetime.fromisoformat(
            scheduler.get_next_run_times().get("back", "")  # type: ignore[arg-type]
        )
        delta = (after - before).total_seconds()
        expected = snooze_minutes * 60
        assert abs(delta - expected) <= 2, f"Expected ~{expected}s, got {delta}s"
    finally:
        scheduler.shutdown()
