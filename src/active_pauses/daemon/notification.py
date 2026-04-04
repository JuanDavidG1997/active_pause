"""libnotify wrapper; action button handling."""
from __future__ import annotations

import logging
import subprocess

from active_pauses.exercises.models import Exercise

logger = logging.getLogger(__name__)

APP_NAME = "active-pauses"


def send_exercise_notification(
    exercise: Exercise,
    scheduler: object,  # MuscleGroupScheduler — avoid circular import
) -> None:
    """Send a libnotify notification for an upcoming exercise.

    Uses notify-send for simplicity (action buttons require a notification daemon
    that supports actions; full dasbus-based notification is in Phase 2).
    """
    title = f"Time for a break! — {exercise.name}"
    body = (
        f"{exercise.verbal_cue}\n"
        f"Duration: {exercise.duration_seconds}s  |  "
        f"Intensity: {'●' * exercise.intensity}{'○' * (3 - exercise.intensity)}"
    )

    try:
        subprocess.run(
            [
                "notify-send",
                "--app-name", APP_NAME,
                "--urgency", "normal",
                "--expire-time", "30000",
                title,
                body,
            ],
            check=True,
            timeout=5,
        )
        logger.info("Notification sent for exercise: %s", exercise.name)
    except FileNotFoundError:
        logger.warning("notify-send not found; skipping notification")
    except subprocess.SubprocessError as e:
        logger.error("Failed to send notification: %s", e)
    except Exception as e:
        logger.error("Unexpected error sending notification: %s", e)
