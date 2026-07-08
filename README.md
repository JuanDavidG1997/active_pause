# active-pauses

**active-pauses** is a Linux health companion that runs quietly in the background and reminds you — a desk worker, programmer, gamer, or anyone who sits for hours — to move. When it's time for a break, an animated avatar walks you through research-backed stretches and exercises, right on your screen. Everything is configured through a browser. All your data stays on your machine, forever.

No cloud. No subscriptions. No root. Just you and your body.

---

## Why active-pauses?

Prolonged sitting is associated with increased risk of musculoskeletal disorders, cardiovascular disease, and metabolic dysfunction (NIOSH, EU-OSHA guidelines). Most reminder tools show a toast notification you dismiss and forget. active-pauses shows you *how* to move — with correct form, breathing cues, and targeted muscle group guidance — then gets out of your way.

---

## Features

### Intelligent Break Scheduling
- Per-muscle-group timers: back, neck, wrists, eyes, legs, full body — each on its own schedule
- Smart suppression: pauses when you're in a fullscreen app, on a video call, or in a calendar event
- Pomodoro-aware: aligns break prompts with your 25-minute work cycles
- Standing desk support: sit/stand ratio guidance, 45-minute continuous standing alert

### Research-Backed Exercise Library
- 20+ built-in exercises from NIOSH, EU-OSHA, and peer-reviewed sources
- Each exercise includes contraindications, intensity level (1–3), and research citation
- Extensible via community exercise packs (TOML format, no code)

### Browser Configuration UI
Open `http://127.0.0.1:7331` in your browser to configure everything:
- Dashboard with today's stats, streaks, and next scheduled pause
- Per-muscle-group timer settings
- Health profile with onboarding questionnaire
- Gamification: streaks, body score, badges, opt-in team leaderboard

### Health Profiles
- Profiles: desk worker, programmer, senior, postpartum, gamer
- 3–5 onboarding questions automatically configure contraindication filters and intensity caps

### Privacy-First
- All data in `~/.local/share/active-pauses/` — your machine, your data
- No telemetry, no analytics sent anywhere
- Calendar sync is 100% optional; OAuth2 tokens stored in your system keyring

---

## Installation

### Option 1: pip (current)

```bash
pip install active-pauses
```

### Option 2: Debian/Ubuntu package (Phase 4)

```bash
wget https://github.com/yourusername/active-pauses/releases/latest/download/active-pauses_1.0.0_amd64.deb
sudo dpkg -i active-pauses_1.0.0_amd64.deb
```

---

## Quick Start

```bash
# Check the daemon is running
active-pauses status

# See all available exercises
active-pauses list-exercises

# Snooze all reminders for 15 minutes
active-pauses snooze 15

# Pause indefinitely (e.g., during a presentation)
active-pauses pause

# Resume
active-pauses resume

# Trigger an exercise right now
active-pauses trigger back_cat_cow

# Run a simulated workday (for testing/development)
active-pauses --simulate 8h
```

---

## Configuration

The config file is `~/.config/active-pauses/config.toml`. It is created automatically on first run with sensible defaults. Changes are picked up automatically within 5 seconds.

**Default config.toml:**
```toml
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
```

---

## Exercise Pack Authoring

Create a file `my_pack/pack.toml`:

```toml
id = "my_yoga_breaks"
name = "Yoga Office Breaks"
version = "1.0.0"
author = "Your Name"
description = "Gentle yoga-inspired breaks for desk workers"
license = "CC-BY-4.0"
```

Create exercises in `my_pack/exercises/yoga.toml`:

```toml
[[exercise]]
id = "seated_spinal_twist"
name = "Seated Spinal Twist"
muscle_groups = ["back"]
intensity = 1
duration_seconds = 45
rest_seconds = 10
animation_ref = "seated_spinal_twist"
research_source = "https://www.cdc.gov/niosh/topics/ergonomics/"
verbal_cue = "Sit tall, twist gently to the right and hold"
bilateral = true

[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Breathe in and sit tall"

[[exercise.phases]]
name = "exhale"
duration_seconds = 5
cue = "Breathe out and gently twist to the right"

[[exercise.phases]]
name = "hold"
duration_seconds = 15
cue = "Hold the twist, breathing naturally"
```

---

## Development

```bash
git clone https://github.com/yourusername/active-pauses
cd active-pauses
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Type check
mypy --strict src/

# Lint
ruff check src/ tests/

# Run simulated workday (development testing)
active-pauses --simulate 8h
```

---

## Architecture

- **Daemon:** Python asyncio process managed by systemd user service
- **IPC:** D-Bus service `org.activepause.Daemon` (dasbus)
- **Scheduling:** APScheduler per-muscle-group interval triggers
- **Storage:** SQLite at `~/.local/share/active-pauses/active_pauses.db` (SQLAlchemy + Alembic)
- **Config:** TOML at `~/.config/active-pauses/config.toml` with inotify hot-reload
- **CLI:** Typer + Rich
- **Web UI (Phase 2):** FastAPI on `127.0.0.1:7331`, Alpine.js frontend
- **Exercise window (Phase 2):** GTK4 with SVG avatar renderer

---

## License

MIT — see [LICENSE](LICENSE)
