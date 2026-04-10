"""Default config values as typed constants."""
from __future__ import annotations

DEFAULT_CONFIG_TOML = """\
# active-pauses configuration
# All intervals are in minutes

[active_hours]
start = "09:00"
end = "18:00"

[notification]
snooze_minutes = 5
urgency = "normal"

[timers.back]
enabled = true
interval_minutes = 45

[timers.neck]
enabled = true
interval_minutes = 45

[timers.wrists]
enabled = true
interval_minutes = 30

[timers.eyes]
enabled = true
interval_minutes = 20

[timers.legs]
enabled = true
interval_minutes = 60

[timers.fullbody]
enabled = true
interval_minutes = 90
"""
