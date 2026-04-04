"""--simulate Nh dry-run mode: accelerated time, no side effects."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from active_pauses import __version__
from active_pauses.config.loader import load_config
from active_pauses.db.engine import get_engine, get_session_factory
from active_pauses.db.models import ExerciseLog, MuscleGroupEnum, WorkSession
from active_pauses.exercises.loader import load_exercise_pack
from active_pauses.exercises.models import MuscleGroup
from active_pauses.exercises.registry import ExerciseRegistry
from active_pauses.exercises.selector import ExerciseSelector

logger = logging.getLogger(__name__)


def parse_duration(spec: str) -> float:
    """Parse '8h', '30m', '2.5h' → float hours."""
    spec = spec.strip().lower()
    if spec.endswith("h"):
        return float(spec[:-1])
    if spec.endswith("m"):
        return float(spec[:-1]) / 60
    raise ValueError(f"Duration must be like '8h' or '30m', got: {spec!r}")


async def run_simulation(
    duration_spec: str,
    config_path: Path | None = None,
    db_url: str | None = None,
    exercises_dir: Path | None = None,
    output_json: Path | None = None,
    speed_factor: float = 10000.0,  # 1 real second = ~167 simulated minutes (8h in ~3s)
) -> list[dict[str, object]]:
    """Run a time-compressed simulation of a full workday.

    Args:
        duration_spec: e.g. '8h' — simulated duration
        config_path: path to config.toml
        db_url: SQLite URL (uses temp if None)
        exercises_dir: path to exercises directory
        output_json: if set, writes event log here
        speed_factor: simulated seconds per real second

    Returns:
        List of event dicts logged during simulation.
    """
    total_hours = parse_duration(duration_spec)
    total_sim_seconds = total_hours * 3600

    config = load_config(config_path)

    # Load exercises
    registry = ExerciseRegistry()
    if exercises_dir and exercises_dir.exists():
        exercises = load_exercise_pack(exercises_dir)
        registry.register(exercises)
    logger.info("Loaded %d exercises for simulation", len(registry))

    selector = ExerciseSelector()

    # Set up DB — create schema directly for simulation
    from active_pauses.db.models import Base

    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)

    events: list[dict[str, object]] = []

    with session_factory() as db_session:
        # Create work session
        sim_start = datetime.now(tz=UTC)
        ws = WorkSession(
            started_at=sim_start,
            daemon_version=__version__,
        )
        db_session.add(ws)
        db_session.commit()
        session_id = ws.id

        # Calculate fire times for each group
        fire_schedule: list[tuple[float, str]] = []  # (sim_second, group)

        for group_name, timer_cfg in config.timers.items():
            if not timer_cfg.enabled:
                continue
            interval_sec = timer_cfg.interval_minutes * 60
            t = interval_sec  # First fire after one interval
            while t <= total_sim_seconds:
                fire_schedule.append((t, group_name))
                t += interval_sec

        # Sort by time
        fire_schedule.sort(key=lambda x: x[0])

        # Simulate: sleep real_sleep = sim_step / speed_factor between events
        logger.info(
            "Simulating %s (%d events) at %.0fx speed",
            duration_spec,
            len(fire_schedule),
            speed_factor,
        )

        last_sim_t = 0.0
        for sim_t, group_name in fire_schedule:
            # Sleep real time for the gap
            real_gap = (sim_t - last_sim_t) / speed_factor
            if real_gap > 0.001:
                await asyncio.sleep(real_gap)
            last_sim_t = sim_t

            # Select exercise
            try:
                group = MuscleGroup(group_name)
            except ValueError:
                logger.warning("Unknown group: %s", group_name)
                continue

            exercise = selector.select(
                registry.all(), group, contraindications=[], intensity_cap=3
            )

            event_time = sim_start + timedelta(seconds=sim_t)
            event: dict[str, object] = {
                "sim_time": sim_t,
                "wall_time": event_time.isoformat(),
                "group": group_name,
                "exercise_id": exercise.id if exercise else None,
                "exercise_name": exercise.name if exercise else None,
                "outcome": "completed" if exercise else "no_exercise_available",
            }
            events.append(event)

            if exercise:
                # Log to DB
                log_entry = ExerciseLog(
                    session_id=session_id,
                    exercise_id=exercise.id,
                    exercise_name=exercise.name,
                    muscle_group=MuscleGroupEnum(group_name),
                    intensity=exercise.intensity,
                    outcome="completed",
                    scheduled_at=event_time,
                    started_at=event_time,
                    completed_at=event_time + timedelta(seconds=exercise.duration_seconds),
                    actual_duration_seconds=exercise.duration_seconds,
                )
                db_session.add(log_entry)
                logger.info(
                    "[t+%.0fs] %s → %s (%s)",
                    sim_t,
                    group_name,
                    exercise.name,
                    event["outcome"],
                )

        # End work session
        ws.ended_at = sim_start + timedelta(seconds=total_sim_seconds)
        db_session.commit()

    if output_json:
        output_json.write_text(json.dumps(events, indent=2), encoding="utf-8")
        logger.info("Event log written to %s", output_json)

    logger.info(
        "Simulation complete: %d events in %.1f simulated hours",
        len(events),
        total_hours,
    )
    return events


def run_simulation_sync(
    duration_spec: str,
    config_path: Path | None = None,
    db_url: str | None = None,
    exercises_dir: Path | None = None,
    output_json: Path | None = None,
) -> list[dict[str, object]]:
    """Synchronous wrapper for run_simulation."""
    return asyncio.run(
        run_simulation(
            duration_spec,
            config_path=config_path,
            db_url=db_url,
            exercises_dir=exercises_dir,
            output_json=output_json,
        )
    )
