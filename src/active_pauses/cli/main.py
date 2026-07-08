"""Typer CLI: start, stop, status, snooze, skip, pause, resume, list-exercises, trigger."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from active_pauses import __version__

app = typer.Typer(
    name="active-pauses",
    help="Linux health companion: reminder to take active breaks.",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dbus_call(method: str, *args: str) -> str | None:
    """Call a DBus method on org.activepause.Daemon via gdbus."""
    cmd = [
        "gdbus",
        "call",
        "--session",
        "--dest", "org.activepause.Daemon",
        "--object-path", "/org/activepause/Daemon",
        "--method", f"org.activepause.Daemon.{method}",
    ] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except FileNotFoundError:
        err_console.print("[red]gdbus not found. Is dbus installed?[/red]")
        return None
    except subprocess.TimeoutExpired:
        err_console.print("[red]DBus call timed out. Is the daemon running?[/red]")
        return None


def _daemon_running() -> bool:
    return _dbus_call("GetStatus") is not None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def start(
    foreground: bool = typer.Option(False, "--foreground", "-f", help="Run in foreground"),
) -> None:
    """Start the active-pauses daemon."""
    if _daemon_running():
        console.print("[yellow]Daemon is already running.[/yellow]")
        raise typer.Exit(0)

    if foreground:
        from active_pauses.daemon.main import run_daemon
        run_daemon()
    else:
        console.print("[green]Use: systemctl --user start active-pauses[/green]")


@app.command()
def stop() -> None:
    """Stop the active-pauses daemon."""
    if not _daemon_running():
        console.print("[yellow]Daemon is not running.[/yellow]")
        raise typer.Exit(0)
    _dbus_call("Quit")
    console.print("Daemon stop requested.")


@app.command()
def status() -> None:
    """Show daemon status."""
    raw = _dbus_call("GetStatus")
    if raw is None:
        console.print("[red]Daemon is not running.[/red]")
        raise typer.Exit(1)

    inner = raw.strip()
    if inner.startswith("('") and inner.endswith("',)"):
        inner = inner[2:-3]
    elif inner.startswith("(") and inner.endswith(",)"):
        inner = inner[1:-2].strip().strip("'\"")

    try:
        data: dict[str, object] = json.loads(inner)
    except json.JSONDecodeError:
        console.print(f"Status: {raw}")
        return

    table = Table(title="active-pauses status")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Running", str(data.get("running", "?")))
    table.add_row("Paused", str(data.get("paused", "?")))
    table.add_row("Completed today", str(data.get("completed_today", 0)))

    next_times = data.get("next_pause_times", {})
    if isinstance(next_times, dict):
        for group, t in sorted(next_times.items()):
            table.add_row(f"Next: {group}", str(t) if t else "—")

    console.print(table)


@app.command()
def snooze(
    minutes: int = typer.Argument(15, help="Minutes to snooze (default: 15)"),
) -> None:
    """Snooze all exercise timers by N minutes."""
    _dbus_call("SnoozeMinutes", str(minutes))
    console.print(f"Snoozed all timers by {minutes} minutes.")


@app.command()
def skip() -> None:
    """Skip the current pending exercise."""
    _dbus_call("SnoozeMinutes", "0")
    console.print("Skipped current exercise.")


@app.command()
def pause() -> None:
    """Pause the exercise scheduler."""
    _dbus_call("Pause")
    console.print("Scheduler paused.")


@app.command()
def resume() -> None:
    """Resume the exercise scheduler."""
    _dbus_call("Resume")
    console.print("Scheduler resumed.")


@app.command(name="list-exercises")
def list_exercises(
    muscle_group: str | None = typer.Option(
        None, "--muscle-group", "-m", help="Filter by muscle group"
    ),
    exercises_dir: Path | None = typer.Option(
        None, "--exercises-dir", help="Path to exercises directory"
    ),
) -> None:
    """List all loaded exercises."""
    import os

    from active_pauses.exercises.loader import load_exercise_pack
    from active_pauses.exercises.models import MuscleGroup

    if exercises_dir is None:
        data_dir = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )
        exercises_dir = data_dir / "active-pauses" / "exercises"

    if not exercises_dir.exists():
        here = Path(__file__).parent.parent.parent.parent.parent
        exercises_dir = here / "exercise_packs" / "builtin" / "exercises"

    if not exercises_dir.exists():
        err_console.print(f"[red]Exercises directory not found: {exercises_dir}[/red]")
        raise typer.Exit(1)

    exercises = load_exercise_pack(exercises_dir)

    if muscle_group:
        try:
            group_enum = MuscleGroup(muscle_group)
            exercises = [ex for ex in exercises if group_enum in ex.muscle_groups]
        except ValueError:
            err_console.print(f"[red]Unknown muscle group: {muscle_group}[/red]")
            raise typer.Exit(1)

    table = Table(title=f"Exercises ({len(exercises)} total)")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Groups")
    table.add_column("Intensity")
    table.add_column("Duration")

    for ex in exercises:
        table.add_row(
            ex.id,
            ex.name,
            ", ".join(g.value for g in ex.muscle_groups),
            "●" * ex.intensity + "○" * (3 - ex.intensity),
            f"{ex.duration_seconds}s",
        )

    console.print(table)


@app.command()
def trigger(
    exercise_id: str = typer.Argument(..., help="Exercise ID to trigger"),
) -> None:
    """Trigger a specific exercise immediately."""
    _dbus_call("TriggerExercise", exercise_id)
    console.print(f"Triggered exercise: {exercise_id}")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit"),
) -> None:
    """active-pauses: Linux health companion daemon."""
    if version:
        console.print(f"active-pauses {__version__}")
        raise typer.Exit(0)
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
