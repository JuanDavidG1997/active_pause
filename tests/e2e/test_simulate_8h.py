"""End-to-end test for --simulate Nh dry-run mode."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from active_pauses.daemon.simulate import run_simulation_sync


@pytest.fixture()
def builtin_exercises_dir() -> Path:
    """Path to the built-in exercises directory."""
    here = Path(__file__).parent.parent.parent
    return here / "exercise_packs" / "builtin" / "exercises"


def test_simulate_8h_completes_quickly(tmp_path: Path, builtin_exercises_dir: Path) -> None:
    """--simulate 8h completes in under 10 seconds."""
    db_url = f"sqlite:///{tmp_path / 'sim.db'}"
    output_json = tmp_path / "events.json"

    t0 = time.monotonic()
    events = run_simulation_sync(
        "8h",
        db_url=db_url,
        exercises_dir=builtin_exercises_dir,
        output_json=output_json,
    )
    elapsed = time.monotonic() - t0

    assert elapsed < 10.0, f"Simulation took {elapsed:.1f}s (must be <10s)"
    assert len(events) > 0, "Simulation produced no events"


def test_simulate_produces_events(tmp_path: Path, builtin_exercises_dir: Path) -> None:
    """Simulation produces events for all enabled muscle groups."""
    db_url = f"sqlite:///{tmp_path / 'sim2.db'}"
    events = run_simulation_sync(
        "2h",
        db_url=db_url,
        exercises_dir=builtin_exercises_dir,
    )

    groups_seen = {e["group"] for e in events}
    # 2h should hit at minimum: eyes (every 20m = 6x), wrists (every 30m = 4x)
    assert "eyes" in groups_seen
    assert "wrists" in groups_seen


def test_simulate_writes_json_output(tmp_path: Path, builtin_exercises_dir: Path) -> None:
    """Simulation writes a valid JSON event log when --output-json is set."""
    import json

    db_url = f"sqlite:///{tmp_path / 'sim3.db'}"
    output_json = tmp_path / "events.json"

    run_simulation_sync(
        "1h",
        db_url=db_url,
        exercises_dir=builtin_exercises_dir,
        output_json=output_json,
    )

    assert output_json.exists()
    events = json.loads(output_json.read_text())
    assert isinstance(events, list)
    if events:
        assert "sim_time" in events[0]
        assert "group" in events[0]
        assert "exercise_id" in events[0]


def test_simulate_no_notifications(
    tmp_path: Path, builtin_exercises_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Simulation never calls notify-send or opens GTK windows."""
    import subprocess

    real_run = subprocess.run
    notify_calls: list[str] = []

    def mock_run(args: list[str], **kwargs: object) -> object:
        if isinstance(args, list) and args and args[0] == "notify-send":
            notify_calls.append(str(args))
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)

    db_url = f"sqlite:///{tmp_path / 'sim4.db'}"
    run_simulation_sync("30m", db_url=db_url, exercises_dir=builtin_exercises_dir)

    assert len(notify_calls) == 0, f"notify-send was called: {notify_calls}"
