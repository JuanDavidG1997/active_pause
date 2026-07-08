# active-pauses: Full Project Blueprint

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade Linux health companion daemon that reminds desk workers to take research-backed active breaks, guided by animated SVG avatars, configured via a localhost web UI, with gamification and analytics — fully offline, no root required, all data local.

**Architecture:** A systemd user service (Python asyncio daemon) manages all scheduling, IPC via DBus, and exercise delivery. A FastAPI localhost server (port 7331) serves the configuration web UI. Exercise windows render in GTK4 with modular SVG avatars. All state lives in SQLite under `~/.local/share/active-pauses/`.

**Tech Stack:** Python 3.12+, asyncio, dbus-python/dasbus, GTK4/PyGObject, FastAPI, SQLAlchemy 2.x + Alembic, APScheduler, libnotify, tomllib/tomli-w, Click/Typer, Alpine.js, ruff, black, mypy strict, pytest/hypothesis

---

## SCOPE & SUB-PLAN MAP

This blueprint covers 9 independent subsystems. During execution, each becomes its own sub-plan:

| Sub-plan | Subsystem | Phase |
|----------|-----------|-------|
| SP-01 | Daemon core + DBus IPC + systemd service | 1 |
| SP-02 | CLI client (Click/Typer) | 1 |
| SP-03 | SQLite schema + Alembic migrations | 1 |
| SP-04 | Exercise library + TOML format + seed data | 1 |
| SP-05 | GTK4 exercise window + SVG avatar renderer | 2 |
| SP-06 | FastAPI localhost web UI (backend + frontend) | 2 |
| SP-07 | Smart scheduling (fullscreen detect, calendar) | 3 |
| SP-08 | Gamification + analytics + reporting | 3 |
| SP-09 | Plugin/exercise pack system | 3 |
| SP-10 | Packaging (.deb, Snap, PyPI) + CI/CD | 4 |

---

# SECTION 1: PHASED ROADMAP

---

## Phase 1 — Daemon Foundation & Core Loop
**Duration:** 5 developer-weeks (1 senior + 1 mid)
**Goal:** A working background daemon that notifies the user to take breaks on configurable schedules, reads TOML config, persists session data to SQLite, and is controllable via a CLI. No GUI yet — libnotify notifications only.

### Features Delivered
- `active-pauses` systemd user service (Python asyncio)
- DBus service `org.activepause.Daemon` with methods: `Pause()`, `Resume()`, `SnoozeMinutes(n)`, `GetStatus()`, `TriggerExercise(exercise_id)`, `Quit()`
- Per-muscle-group timer configuration via `~/.config/active-pauses/config.toml`
- Exercise library loader: reads TOML exercise packs from `~/.local/share/active-pauses/exercises/`
- 20 seed exercises across 6 muscle groups (back, neck, wrists, eyes, legs, full-body)
- `active-pauses` CLI: `start`, `stop`, `status`, `snooze [minutes]`, `skip`, `pause`, `resume`, `list-exercises`, `trigger <exercise_id>`
- libnotify notifications with action buttons (Do it now / Snooze 5m / Skip)
- SQLite schema v1: sessions, exercises_log, config_snapshots
- Alembic migration baseline
- `--simulate 8h` dry-run mode for testing

### Acceptance Criteria
- [ ] `systemctl --user start active-pauses` starts the daemon without root
- [ ] Daemon fires a libnotify notification at the configured interval per muscle group
- [ ] `active-pauses status` prints daemon state, next scheduled pause times, and today's completion count
- [ ] `active-pauses snooze 10` delays all timers 10 minutes; notification confirms
- [ ] Config change in `config.toml` is picked up within 5 seconds (inotify watch)
- [ ] `active-pauses --simulate 8h` runs a full day in <10 seconds, logs all planned events to stdout without side effects
- [ ] All 20 seed exercises load without error and validate against TOML schema
- [ ] `mypy --strict` passes with 0 errors
- [ ] `pytest` passes with ≥80% line coverage on daemon core

### Dependencies
- None (greenfield)

---

## Phase 2 — Visual Experience: GTK4 Window + Web UI MVP
**Duration:** 7 developer-weeks
**Goal:** Users see animated avatar exercise windows and can configure everything via a localhost browser UI. The product is usable as a daily driver.

### Features Delivered
- GTK4 exercise window: full-screen-capable overlay, auto-dismiss timer, progress bar
- Modular SVG avatar system: 4 base bodies × 5 skin tones = 20 base variants; 6 muscle-group highlight overlays; clothing layer; face/hair layer
- CSS keyframe animations for each of the 20 seed exercises; reduced-motion fallback
- FastAPI server on `127.0.0.1:7331` launched as part of the daemon
- Web UI pages: Dashboard, Timer Configuration, Profile Setup (onboarding), Exercise Library Browser
- Health profiles: `desk_worker`, `programmer`, `senior`, `postpartum`, `gamer` — with onboarding questionnaire mapping to contraindication flags + intensity cap
- Standing desk sit/stand ratio tracker (configurable ratio, 45-min standing alert)
- Avatar selection in profile (gender expression + skin tone)
- `active-pauses web` CLI command opens the default browser to `http://127.0.0.1:7331`

### Acceptance Criteria
- [ ] Exercise window appears within 2 seconds of notification "Do it now" click
- [ ] Avatar correctly highlights the active muscle group during exercise (visible overlay layer)
- [ ] `prefers-reduced-motion` CSS media query disables CSS keyframe animations; static pose shown
- [ ] Web UI loads in Firefox 124+ and Chromium 124+ with no build step, no console errors
- [ ] Onboarding questionnaire (3–5 questions) persists profile; daemon respects contraindication filter
- [ ] Standing desk toggle in web UI starts/stops sit/stand timer; 45-min standing triggers notification
- [ ] All 8 API endpoints from Section 9 Phase-2 subset return correct data and validate with pytest
- [ ] `mypy --strict` and `ruff check` pass with 0 errors

### Dependencies
- Phase 1 complete (daemon, SQLite, exercise library)

---

## Phase 3 — Smart Scheduling, Gamification & Analytics
**Duration:** 6 developer-weeks
**Goal:** The app becomes smart and sticky. It respects the user's context (calendar, fullscreen), rewards consistency, and provides actionable health insights.

### Features Delivered
- Fullscreen app detection (X11 via python-xlib; Wayland via wlr-foreign-toplevel protocol or D-Bus org.gnome.Shell)
- Calendar integration: Google Calendar API (OAuth2 PKCE) + Nextcloud CalDAV — suppress notifications during events
- Pomodoro integration: detect 25-min work cycles, align break prompts with Pomodoro breaks
- Tokens stored in libsecret via secretstorage Python library
- Gamification: streak counter, body score (0–100, weighted by muscle group coverage), 15 badges, opt-in team leaderboard via shared 32-char token
- Web UI pages: Gamification/Team Board, Analytics & Reports (Chart.js charts, CSV export), Plugin/Pack Manager, Accessibility Settings, Calendar Integration Setup
- Weekly report: `active-pauses report --week` prints ASCII table + emails optional HTML report if SMTP configured
- SQLite analytics views for posture score trend, muscle group coverage heatmap
- Plugin/exercise pack system: install from local `.tar.gz` or URL, validate TOML schema, enable/disable
- All remaining API endpoints (Section 9)

### Acceptance Criteria
- [ ] Daemon does NOT fire notification when a fullscreen window is detected (tested with a mock X11 fullscreen signal)
- [ ] After connecting Google Calendar, events show in dashboard; notifications suppressed during test event
- [ ] OAuth2 PKCE flow completes in browser, token stored in libsecret, survives daemon restart
- [ ] Streak increments on consecutive days with ≥2 completed exercises; resets after 48h gap
- [ ] Body score calculation matches specification formula (Section 8 gamification)
- [ ] `active-pauses report --week` exits 0 and prints non-empty output
- [ ] Plugin pack install validates TOML schema and rejects packs with `exec`, `import`, or `script` keys
- [ ] All web UI pages render without JS errors in Firefox and Chromium
- [ ] `pytest` passes ≥85% line coverage; hypothesis property tests pass with 100 examples

### Dependencies
- Phase 1 and Phase 2 complete

---

## Phase 4 — Polish, Packaging & Launch
**Duration:** 4 developer-weeks
**Goal:** Production-quality packaging, accessibility audit, documentation, and CI/CD pipeline. Ready for v1.0 release.

### Features Delivered
- `.deb` package (Ubuntu 24.04 focal/noble) with `postinst` systemd user service enablement
- Snap package (`snapcraft.yaml`, strict confinement, pulseaudio + desktop interfaces)
- PyPI package (`pyproject.toml`, `build` backend, `pip install active-pauses`)
- GitHub Actions: PR checks (ruff, mypy, pytest), merge-to-main checks (integration tests), release-tag workflow (build all 3 artifacts, create GitHub Release with auto-generated changelog)
- Full accessibility audit: axe-core for web UI, AT-SPI for GTK4 window, audio cues for all exercises
- Screen reader support: GTK4 accessible labels, ARIA labels in web UI
- Reduced-motion mode: daemon setting, propagated to both GTK and web UI
- Documentation site (MkDocs Material): architecture, API reference, exercise pack authoring
- Localization scaffold: `gettext` for daemon/CLI/GTK; English strings externalized
- Final README, CONTRIBUTING.md, SECURITY.md, CHANGELOG.md

### Acceptance Criteria
- [ ] `dpkg -i active-pauses_1.0.0_amd64.deb` installs cleanly on Ubuntu 24.04; `systemctl --user status active-pauses` shows active
- [ ] `snap install active-pauses_1.0.0_amd64.snap --dangerous` installs and runs
- [ ] `pip install active-pauses` in a fresh venv installs and `active-pauses --version` prints `1.0.0`
- [ ] GitHub Actions release workflow succeeds on tag `v1.0.0` and attaches all 3 artifacts to GitHub Release
- [ ] axe-core audit of web UI reports 0 critical violations
- [ ] NVDA/Orca reads exercise instructions in correct order in GTK4 window
- [ ] All `mypy --strict`, `ruff check --select ALL`, `pytest` pass in CI

### Dependencies
- Phase 1, 2, and 3 complete

---

# SECTION 2: FULL REPOSITORY STRUCTURE

```
active-pauses/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml          # GitHub issue form for bug reports
│   │   ├── feature_request.yml     # GitHub issue form for feature requests
│   │   └── exercise_pack.yml       # GitHub issue form for exercise pack submissions
│   ├── PULL_REQUEST_TEMPLATE/
│   │   ├── feature.md              # PR template for new features
│   │   ├── bugfix.md               # PR template for bug fixes
│   │   ├── exercise_pack.md        # PR template for exercise pack additions
│   │   ├── avatar_asset.md         # PR template for avatar/animation assets
│   │   └── dependency_update.md    # PR template for dependency bumps
│   └── workflows/
│       ├── pr-checks.yml           # On PR: ruff, mypy, pytest unit+integration
│       ├── merge-main.yml          # On merge to main: full test suite + coverage gate
│       └── release.yml             # On tag v*: build .deb, .snap, PyPI wheel, create GH Release
│
├── src/
│   └── active_pauses/
│       ├── __init__.py             # Package version export: __version__ = "1.0.0"
│       ├── __main__.py             # Entry point for `python -m active_pauses`
│       │
│       ├── daemon/
│       │   ├── __init__.py
│       │   ├── main.py             # asyncio event loop entry point; wires all subsystems
│       │   ├── scheduler.py        # APScheduler-based per-muscle-group timer manager
│       │   ├── ipc.py              # DBus service org.activepause.Daemon (dasbus)
│       │   ├── notification.py     # libnotify wrapper; action button handling
│       │   ├── config_watcher.py   # inotify watch on config.toml; triggers reload
│       │   ├── standing_tracker.py # Sit/stand ratio logic; 45-min continuous standing detection
│       │   ├── fullscreen.py       # X11/Wayland fullscreen app detection
│       │   ├── pomodoro.py         # Pomodoro cycle detection and alignment
│       │   └── simulate.py         # --simulate Nh dry-run mode; replays 8h in <10s
│       │
│       ├── calendar_sync/
│       │   ├── __init__.py
│       │   ├── base.py             # Abstract CalendarProvider protocol
│       │   ├── google_cal.py       # Google Calendar API client (OAuth2 PKCE)
│       │   ├── caldav_client.py    # Nextcloud CalDAV client (requests + vobject)
│       │   ├── token_store.py      # libsecret/secretstorage token persistence
│       │   └── event_cache.py      # In-memory + SQLite cache of upcoming events
│       │
│       ├── exercises/
│       │   ├── __init__.py
│       │   ├── models.py           # Pydantic v2 models: Exercise, ExercisePhase, MuscleGroup
│       │   ├── loader.py           # Loads and validates TOML exercise packs
│       │   ├── selector.py         # Selects exercise based on profile, contraindications, recency
│       │   ├── schema.py           # TOML schema validation (pydantic + custom validators)
│       │   └── registry.py         # Singleton registry of all loaded exercises
│       │
│       ├── avatars/
│       │   ├── __init__.py
│       │   ├── renderer.py         # Composites SVG layers for a given profile + exercise
│       │   ├── animation.py        # Maps exercise_id → CSS keyframe animation name
│       │   └── models.py           # Avatar dataclass: gender_expr, skin_tone, clothing
│       │
│       ├── window/
│       │   ├── __init__.py
│       │   ├── exercise_window.py  # GTK4 ApplicationWindow: avatar, timer, instruction text
│       │   ├── progress_bar.py     # GTK4 ProgressBar with countdown logic
│       │   └── accessibility.py    # AT-SPI accessible names and descriptions for GTK widgets
│       │
│       ├── web/
│       │   ├── __init__.py
│       │   ├── app.py              # FastAPI app factory; mounts routes and static files
│       │   ├── server.py           # uvicorn launcher bound to 127.0.0.1:7331
│       │   ├── auth.py             # Single-use session token for web UI (see security model)
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── dashboard.py    # GET /api/dashboard
│       │   │   ├── timers.py       # GET/PUT /api/timers
│       │   │   ├── profile.py      # GET/PUT /api/profile, POST /api/profile/onboarding
│       │   │   ├── exercises.py    # GET /api/exercises, GET /api/exercises/{id}
│       │   │   ├── standing.py     # GET/PUT /api/standing
│       │   │   ├── gamification.py # GET /api/gamification, POST /api/gamification/team
│       │   │   ├── analytics.py    # GET /api/analytics/*, GET /api/analytics/export
│       │   │   ├── plugins.py      # GET/POST/DELETE /api/plugins
│       │   │   ├── accessibility.py# GET/PUT /api/accessibility
│       │   │   └── calendar.py     # GET/POST/DELETE /api/calendar
│       │   └── static/
│       │       ├── index.html      # Single-page shell; Alpine.js routing
│       │       ├── app.js          # Alpine.js component definitions (all UI logic)
│       │       ├── style.css       # CSS custom properties + layout (no framework)
│       │       ├── chart.min.js    # Chart.js 4.x vendored (no CDN; offline-first)
│       │       └── alpine.min.js   # Alpine.js 3.x vendored
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   ├── engine.py           # SQLAlchemy engine + session factory
│       │   ├── models.py           # All SQLAlchemy ORM models (see Section 10)
│       │   ├── repositories/
│       │   │   ├── __init__.py
│       │   │   ├── session_repo.py # CRUD for work_sessions table
│       │   │   ├── exercise_log_repo.py # CRUD for exercise_log table
│       │   │   ├── profile_repo.py # CRUD for user_profile table
│       │   │   └── analytics_repo.py   # Aggregate queries for analytics endpoints
│       │   └── migrations/
│       │       ├── env.py          # Alembic env.py referencing engine.py
│       │       ├── script.py.mako  # Alembic migration script template
│       │       └── versions/
│       │           └── 0001_initial_schema.py # Baseline Alembic migration
│       │
│       ├── gamification/
│       │   ├── __init__.py
│       │   ├── streak.py           # Streak calculation logic
│       │   ├── body_score.py       # Body score (0–100) weighted formula
│       │   ├── badges.py           # Badge definitions and award logic
│       │   └── leaderboard.py      # Team leaderboard via shared token (local aggregation)
│       │
│       ├── analytics/
│       │   ├── __init__.py
│       │   ├── reporter.py         # Weekly report generator (ASCII + HTML)
│       │   └── exporter.py         # CSV export of exercise_log + sessions
│       │
│       ├── plugins/
│       │   ├── __init__.py
│       │   ├── installer.py        # Download + extract .tar.gz plugin packs
│       │   ├── validator.py        # TOML schema validation; rejects exec/import/script keys
│       │   └── registry.py         # Tracks installed + enabled packs
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py             # Typer CLI: start, stop, status, snooze, skip, etc.
│       │
│       └── config/
│           ├── __init__.py
│           ├── schema.py           # Pydantic models for config.toml structure
│           ├── defaults.py         # Default config values as typed constants
│           └── loader.py           # tomllib loader + writer (tomli-w)
│
├── tests/
│   ├── conftest.py                 # Shared fixtures: tmp config dir, in-memory SQLite, mock dbus
│   ├── unit/
│   │   ├── test_scheduler.py       # Timer logic, interval calculation, snooze math
│   │   ├── test_exercise_selector.py # Selection algorithm, contraindication filtering
│   │   ├── test_exercise_loader.py # TOML parsing, schema validation, error cases
│   │   ├── test_streak.py          # Streak calculation edge cases
│   │   ├── test_body_score.py      # Body score formula; hypothesis property tests
│   │   ├── test_standing_tracker.py# Sit/stand ratio; 45-min detection
│   │   ├── test_config_loader.py   # TOML load/write roundtrip; defaults merge
│   │   ├── test_plugin_validator.py# Accept valid packs; reject forbidden keys
│   │   └── test_reporter.py        # Weekly report output; CSV export format
│   ├── integration/
│   │   ├── test_ipc.py             # DBus method calls against live daemon (subprocess)
│   │   ├── test_web_api.py         # FastAPI TestClient against all 30+ endpoints
│   │   ├── test_db_migrations.py   # Alembic upgrade head on fresh DB; schema matches models
│   │   └── test_calendar_sync.py   # Mock OAuth2 server; verify token storage + event cache
│   ├── e2e/
│   │   ├── test_simulate_8h.py     # --simulate 8h; verify event log, no side effects
│   │   └── test_onboarding_flow.py # Full onboarding → first exercise notification flow
│   └── snapshots/
│       ├── test_avatar_renderer.py # Snapshot tests for SVG composite output
│       └── __snapshots__/
│           └── *.svg               # Reference SVG snapshots (committed)
│
├── assets/
│   ├── avatars/
│   │   ├── README.md               # Avatar layer naming convention + authoring guide
│   │   ├── base/
│   │   │   ├── body_masc_s1.svg    # Masculine body, skin tone 1 (Fitzpatrick I-II)
│   │   │   ├── body_masc_s2.svg    # Masculine body, skin tone 2
│   │   │   ├── body_masc_s3.svg    # Masculine body, skin tone 3
│   │   │   ├── body_masc_s4.svg    # Masculine body, skin tone 4
│   │   │   ├── body_masc_s5.svg    # Masculine body, skin tone 5 (Fitzpatrick V-VI)
│   │   │   ├── body_femm_s1.svg    # Feminine body, skin tone 1
│   │   │   ├── body_femm_s2.svg
│   │   │   ├── body_femm_s3.svg
│   │   │   ├── body_femm_s4.svg
│   │   │   ├── body_femm_s5.svg
│   │   │   ├── body_nbin_s1.svg    # Non-binary body, skin tone 1
│   │   │   ├── body_nbin_s2.svg
│   │   │   ├── body_nbin_s3.svg
│   │   │   ├── body_nbin_s4.svg
│   │   │   └── body_nbin_s5.svg    # 15 base body SVGs total
│   │   ├── overlays/
│   │   │   ├── highlight_back.svg  # Muscle highlight overlay: back/spine (semi-transparent)
│   │   │   ├── highlight_neck.svg  # Muscle highlight overlay: neck/trapezius
│   │   │   ├── highlight_wrists.svg# Muscle highlight overlay: wrists/forearms
│   │   │   ├── highlight_eyes.svg  # Eye area highlight overlay
│   │   │   ├── highlight_legs.svg  # Legs/hamstrings/quads highlight overlay
│   │   │   └── highlight_fullbody.svg # Full-body highlight overlay
│   │   ├── clothing/
│   │   │   ├── casual_default.svg  # Default casual clothing layer
│   │   │   └── office_default.svg  # Office attire clothing layer
│   │   └── faces/
│   │       ├── face_a.svg          # Face variant A (neutral expression)
│   │       ├── face_b.svg          # Face variant B
│   │       └── face_c.svg          # Face variant C
│   ├── animations/
│   │   ├── README.md               # Animation authoring: keyframe naming conventions
│   │   ├── back_cat_cow.css        # CSS keyframes for Cat-Cow stretch
│   │   ├── neck_side_tilt.css      # CSS keyframes for neck side tilt
│   │   ├── wrist_circles.css       # CSS keyframes for wrist circles
│   │   ├── eye_palming.css         # CSS keyframes for eye palming
│   │   ├── leg_calf_raises.css     # CSS keyframes for calf raises
│   │   └── ...                     # One CSS file per exercise animation
│   └── audio/
│       ├── README.md               # Audio cue format + accessibility notes
│       ├── bell_start.ogg          # Gentle bell: exercise starting
│       ├── bell_end.ogg            # Gentle bell: exercise complete
│       └── voice/
│           ├── en/
│           │   ├── inhale.ogg      # "Inhale"
│           │   ├── exhale.ogg      # "Exhale"
│           │   └── hold.ogg        # "Hold"
│           └── README.md           # Voice cue authoring guide
│
├── exercise_packs/
│   ├── README.md                   # Exercise pack format and authoring guide
│   ├── builtin/
│   │   ├── pack.toml               # Built-in pack manifest
│   │   └── exercises/
│   │       ├── back.toml           # Back/spine exercises
│   │       ├── neck.toml           # Neck exercises
│   │       ├── wrists.toml         # Wrist/forearm exercises
│   │       ├── eyes.toml           # Eye exercises
│   │       ├── legs.toml           # Leg/lower body exercises
│   │       └── fullbody.toml       # Full-body exercises
│   └── example_community_pack/
│       ├── pack.toml               # Example community pack manifest
│       └── exercises/
│           └── yoga_breaks.toml    # Example community exercise file
│
├── config_schema/
│   ├── config.schema.toml          # Annotated TOML config schema (documentation only)
│   └── exercise.schema.toml        # Annotated exercise TOML schema (documentation only)
│
├── packaging/
│   ├── deb/
│   │   ├── control                 # Debian control file
│   │   ├── postinst                # Post-install script: systemctl --user enable active-pauses
│   │   ├── prerm                   # Pre-remove: systemctl --user disable active-pauses
│   │   └── active-pauses.service   # systemd user service unit file
│   ├── snap/
│   │   └── snapcraft.yaml          # Snapcraft definition for strict confinement
│   └── pyproject.toml              # PEP 517/518 build config; also used for pip install
│
├── docs/
│   ├── superpowers/
│   │   └── plans/
│   │       └── 2026-04-02-active-pauses-blueprint.md  # This document
│   ├── architecture.md             # System architecture overview with diagrams
│   ├── api.md                      # Auto-generated FastAPI docs reference
│   ├── exercise_pack_authoring.md  # Step-by-step guide to writing exercise packs
│   ├── avatar_authoring.md         # Step-by-step guide to creating avatar variants
│   ├── security.md                 # Security model documentation
│   └── mkdocs.yml                  # MkDocs Material configuration
│
├── scripts/
│   ├── dev_setup.sh                # One-shot dev environment setup (Ubuntu 24.04)
│   ├── run_daemon_dev.sh           # Launch daemon in foreground with debug logging
│   └── generate_migrations.sh      # Wrapper: alembic revision --autogenerate
│
├── README.md                       # Project README (see Section 4 for full draft)
├── CONTRIBUTING.md                 # Contributing guide (see Section 5 for full draft)
├── SECURITY.md                     # Vulnerability disclosure policy
├── CHANGELOG.md                    # Conventional Commits changelog
├── LICENSE                         # MIT License
├── pyproject.toml                  # Canonical build + tool config (ruff, mypy, pytest)
└── .python-version                 # 3.12 (used by pyenv/mise)
```

---

# SECTION 3: GITHUB PULL REQUEST TEMPLATES

---

## `.github/PULL_REQUEST_TEMPLATE/feature.md`

```markdown
## Feature: [Short description]

Closes #[issue number]

### What does this PR do?

<!-- 2–4 sentences. What feature is being added? What problem does it solve? -->

### Type of change

- [ ] New feature (non-breaking addition)
- [ ] Breaking change (existing behavior changes — requires migration guide)
- [ ] New exercise pack / avatar asset (use the dedicated template instead)

### Implementation approach

<!-- Brief explanation of the architectural decisions made. Why this approach over alternatives? -->

### Testing done

- [ ] Unit tests added/updated — `pytest tests/unit/ -v` passes
- [ ] Integration tests added/updated — `pytest tests/integration/ -v` passes
- [ ] `--simulate 8h` dry run tested: `active-pauses --simulate 8h`
- [ ] Manually tested on Ubuntu 24.04 with systemd user service running
- [ ] Web UI tested in Firefox and Chromium (if UI changes)

### Screenshots / recordings

<!-- Required for any UI changes (GTK window or web UI). Drag images here or link asciinema recording. -->

### Checklist

- [ ] `mypy --strict src/` passes with 0 errors
- [ ] `ruff check src/ tests/` passes with 0 warnings
- [ ] `black --check src/ tests/` passes
- [ ] All new public functions have docstrings
- [ ] All new functions are type-annotated
- [ ] CHANGELOG.md updated under `[Unreleased]` section
- [ ] `prefers-reduced-motion` respected (if animation changes)
- [ ] No new root-required operations introduced
- [ ] No new network calls outside of explicitly opt-in features (calendar sync)
- [ ] Plugin sandbox: no arbitrary code execution paths added

### Related issues / PRs

<!-- List any related issues or PRs. Use "Closes #N" to auto-close. -->
```

---

## `.github/PULL_REQUEST_TEMPLATE/bugfix.md`

```markdown
## Bug Fix: [Short description]

Fixes #[issue number]

### Root cause

<!-- What caused the bug? Be specific — include the file and line if relevant. -->

### Fix

<!-- How is the bug fixed? 1–3 sentences. -->

### Reproduction steps (before fix)

```
1. 
2. 
3. Expected: ...
   Actual: ...
```

### Testing done

- [ ] Regression test added: `tests/unit/test_[module].py::test_[name]` covers the exact failure
- [ ] `pytest tests/ -v` passes
- [ ] Manually verified fix on Ubuntu 24.04

### Checklist

- [ ] `mypy --strict src/` passes with 0 errors
- [ ] `ruff check src/ tests/` passes
- [ ] The regression test FAILS on the unfixed code (verified)
- [ ] No unrelated changes included in this PR
- [ ] CHANGELOG.md updated under `[Unreleased]` → `Fixed`

### Related issues

Fixes #
```

---

## `.github/PULL_REQUEST_TEMPLATE/exercise_pack.md`

```markdown
## Exercise Pack Addition: [Pack Name]

Closes #[issue number]

### Pack summary

- **Pack name:** 
- **Author / maintainer:** 
- **Target muscle groups:** 
- **Number of exercises:** 
- **Intensity range:** 1 (gentle) – 3 (vigorous)
- **Research sources cited:** (list DOI or URL for each exercise)

### Pack file location

`exercise_packs/[pack_name]/pack.toml`

### Validation

- [ ] `active-pauses validate-pack exercise_packs/[pack_name]/pack.toml` exits 0
- [ ] All exercises have `research_source` field with valid citation
- [ ] All exercises with intensity ≥ 2 have at least one `contraindication` listed
- [ ] Animation reference files exist in `assets/animations/` or pack includes its own
- [ ] Verbal cue text (`verbal_cue`) is under 120 characters per phase
- [ ] No `exec`, `import`, `script`, `shell` keys present anywhere in TOML files

### Testing

- [ ] Pack loads without error via `active-pauses list-exercises --pack [pack_name]`
- [ ] At least 2 exercises manually triggered via `active-pauses trigger [exercise_id]` and tested in exercise window
- [ ] `pytest tests/unit/test_exercise_loader.py -v` passes with new pack

### Screenshots

<!-- Required: screenshot of at least one exercise running in the GTK window with avatar animation. -->

### Checklist

- [ ] All exercises reviewed for medical accuracy by contributor (note: not a substitute for professional medical advice)
- [ ] Contraindications are conservative (err on the side of caution)
- [ ] Exercise names are unique across all packs
- [ ] License for any referenced material is compatible with MIT
```

---

## `.github/PULL_REQUEST_TEMPLATE/avatar_asset.md`

```markdown
## Avatar / Animation Asset: [Description]

Closes #[issue number]

### Asset type

- [ ] New base body variant (gender expression + skin tone)
- [ ] New muscle highlight overlay
- [ ] New clothing layer
- [ ] New face/hair variant
- [ ] New CSS animation (exercise animation)
- [ ] New audio cue

### Files added

<!-- List exact file paths -->

### Naming convention compliance

- [ ] Base body: `body_[expr]_s[1-5].svg` where `expr` ∈ {`masc`, `femm`, `nbin`}
- [ ] Overlay: `highlight_[muscle_group].svg`
- [ ] Animation CSS: `[muscle_group]_[exercise_slug].css`
- [ ] Animation class name in CSS matches `anim-[exercise_id]` convention
- [ ] Audio: `.ogg` format, ≤50ms silence at start/end, ≤200KB

### SVG compliance (for SVG assets)

- [ ] SVG uses `id` attributes on all animatable layers (format: `layer-[name]`)
- [ ] SVG viewBox is `0 0 200 400` (standard avatar canvas)
- [ ] No embedded raster images (pure vector)
- [ ] File size ≤ 50KB (before gzip)
- [ ] Tested in Firefox and Chromium SVG renderer

### CSS animation compliance (for animation CSS)

- [ ] `@media (prefers-reduced-motion: reduce)` block present with static fallback
- [ ] Animation uses `transform` and `opacity` only (no layout-triggering properties)
- [ ] Keyframe names follow `kf-[exercise_id]-[phase]` convention
- [ ] Tested at 30fps minimum on integrated graphics

### Screenshots / previews

<!-- Required: screenshot or short video of the asset rendered in the exercise window. -->

### Checklist

- [ ] Asset is original work or licensed CC0/CC-BY compatible with MIT project
- [ ] Attribution added to `assets/[type]/README.md` if required by license
- [ ] No proprietary fonts or icons embedded in SVG
```

---

## `.github/PULL_REQUEST_TEMPLATE/dependency_update.md`

```markdown
## Dependency Update: [Package name] [old version] → [new version]

### Reason for update

- [ ] Security advisory: [CVE or advisory link]
- [ ] Bug fix in dependency affecting active-pauses
- [ ] New feature needed by active-pauses
- [ ] Scheduled maintenance / keeping current

### Advisory / changelog reference

<!-- Link to release notes or CVE. -->

### Breaking changes in new version

<!-- List any API changes that required code changes in this PR. "None" if no breaking changes. -->

### Files changed (beyond pyproject.toml)

<!-- List any src/ files that required changes due to API changes in the dependency. -->

### Testing done

- [ ] `pytest tests/ -v` passes with new dependency version
- [ ] `mypy --strict src/` passes
- [ ] Manually ran `active-pauses --simulate 8h` to verify no runtime regressions
- [ ] Verified on Ubuntu 24.04 with clean venv

### Checklist

- [ ] Only the target dependency (and its transitive dependencies) changed in lock file
- [ ] `pyproject.toml` version constraint updated appropriately (not over-pinned)
- [ ] No new transitive dependencies with GPL/proprietary licenses introduced
- [ ] CHANGELOG.md updated if this fixes a user-visible bug
```

---

# SECTION 4: README (FULL DRAFT)

```markdown
# active-pauses

<!-- PROJECT LOGO: Replace with actual SVG logo -->
<p align="center">
  <img src="docs/assets/logo.svg" alt="active-pauses logo" width="180"/>
</p>

<p align="center">
  <a href="https://github.com/yourusername/active-pauses/actions/workflows/pr-checks.yml">
    <img src="https://github.com/yourusername/active-pauses/actions/workflows/pr-checks.yml/badge.svg" alt="CI"/>
  </a>
  <a href="https://pypi.org/project/active-pauses/">
    <img src="https://img.shields.io/pypi/v/active-pauses.svg" alt="PyPI version"/>
  </a>
  <a href="https://snapcraft.io/active-pauses">
    <img src="https://snapcraft.io/active-pauses/badge.svg" alt="Snap Store"/>
  </a>
  <img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/platform-Ubuntu%2024.04%2B-orange" alt="Ubuntu 24.04+"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"/>
  <img src="https://img.shields.io/badge/data-100%25%20local-brightgreen" alt="100% local data"/>
</p>

---

**active-pauses** is a Linux health companion that runs quietly in the background and reminds you — a desk worker, programmer, gamer, or anyone who sits for hours — to move. When it's time for a break, an animated avatar walks you through research-backed stretches and exercises, right on your screen. Everything is configured through a browser. All your data stays on your machine, forever.

No cloud. No subscriptions. No root. Just you and your body.

---

## Why active-pauses?

Prolonged sitting is [associated with increased risk of musculoskeletal disorders](https://doi.org/10.1136/bjsports-2018-100078), cardiovascular disease, and metabolic dysfunction (NIOSH, EU-OSHA guidelines). Most reminder tools show a toast notification you dismiss and forget. active-pauses shows you *how* to move — with correct form, breathing cues, and targeted muscle group guidance — then gets out of your way.

---

## Features

### Intelligent Break Scheduling
- Per-muscle-group timers: back, neck, wrists, eyes, legs, full body — each on its own schedule
- Smart suppression: pauses when you're in a fullscreen app, on a video call, or in a calendar event
- Pomodoro-aware: aligns break prompts with your 25-minute work cycles
- Standing desk support: sit/stand ratio guidance (recommended 1:1), 45-minute continuous standing alert

### Guided Exercises with Animated Avatars
<!-- SCREENSHOT PLACEHOLDER: Exercise window with avatar -->
- Animated cartoon avatars guide you through each exercise in real time
- Muscle group highlights show exactly what you're working
- Breathing phase indicators (inhale / exhale / hold)
- Audio cues and full screen-reader support

### Research-Backed Exercise Library
- 20+ built-in exercises from NIOSH, EU-OSHA, and peer-reviewed sources
- Each exercise includes contraindications, intensity level (1–3), and research citation
- Extensible via community exercise packs (TOML format, no code)

### Browser Configuration UI
<!-- SCREENSHOT PLACEHOLDER: Web UI dashboard -->
Open `http://127.0.0.1:7331` in your browser to configure everything:
- Dashboard with today's stats, streaks, and next scheduled pause
- Per-muscle-group timer settings
- Health profile with onboarding questionnaire
- Exercise library browser with filtering by muscle group, intensity, and contraindication
- Gamification: streaks, body score, badges, opt-in team leaderboard
- Analytics: weekly reports, posture score trends, CSV export

### Health Profiles
- Profiles: desk worker, programmer, senior, postpartum, gamer
- 3–5 onboarding questions automatically configure contraindication filters and intensity caps
- Profile can be updated anytime via the web UI

### Gamification
- Daily streaks and body score (0–100)
- 15 achievement badges
- Opt-in team leaderboard (shared via a token — no server required)

### Privacy-First
- All data in `~/.local/share/active-pauses/` — your machine, your data
- No telemetry, no analytics sent anywhere
- Calendar sync is 100% optional; OAuth2 tokens stored in your system keyring

---

## Installation

### Option 1: Debian/Ubuntu package (recommended)

```bash
wget https://github.com/yourusername/active-pauses/releases/latest/download/active-pauses_1.0.0_amd64.deb
sudo dpkg -i active-pauses_1.0.0_amd64.deb
```

The package automatically enables the systemd user service.

### Option 2: Snap

```bash
snap install active-pauses
```

### Option 3: pip

```bash
pip install active-pauses
# Then enable the systemd service:
active-pauses install-service
```

---

## Quick Start

```bash
# Check the daemon is running
active-pauses status

# Open the configuration UI in your browser
active-pauses web

# Trigger an exercise right now
active-pauses trigger neck_side_tilt

# See all available exercises
active-pauses list-exercises

# Snooze all reminders for 15 minutes
active-pauses snooze 15

# Pause indefinitely (e.g., during a presentation)
active-pauses pause

# Resume
active-pauses resume
```

After installation, the daemon starts automatically on login. Open `http://127.0.0.1:7331` in your browser to configure your profile and timers.

---

## Configuration

All configuration is done through the web UI at `http://127.0.0.1:7331`. Open it with:

```bash
active-pauses web
```

The underlying config file is `~/.config/active-pauses/config.toml` — you can edit it directly if you prefer. Changes are picked up automatically within 5 seconds.

**Example config.toml:**
```toml
[timers]
back_interval_minutes = 45
neck_interval_minutes = 30
wrists_interval_minutes = 20
eyes_interval_minutes = 20
legs_interval_minutes = 60
fullbody_interval_minutes = 90

[profile]
type = "programmer"
intensity_cap = 2
reduced_motion = false

[standing_desk]
enabled = true
sit_stand_ratio = "1:1"
max_standing_minutes = 45

[notifications]
audio_cues = true
screen_reader_mode = false
```

---

## Exercise Pack Authoring

Create a file `my_pack/pack.toml`:

```toml
[pack]
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
muscle_groups = ["back", "neck"]
intensity = 1
duration_seconds = 30
rest_seconds = 10
hold_seconds = 15
contraindications = ["spinal_surgery", "herniated_disc_acute"]
animation_ref = "back_seated_twist"
research_source = "NIOSH Publication 97-117"
verbal_cue = "Sit tall, place right hand on left knee, twist gently to the left"

[[exercise.phases]]
name = "inhale"
duration_seconds = 4
cue = "Breathe in and sit tall"

[[exercise.phases]]
name = "twist"
duration_seconds = 15
cue = "Exhale and rotate gently to the left"

[[exercise.phases]]
name = "hold"
duration_seconds = 11
cue = "Hold and breathe naturally"
```

Install your pack:
```bash
active-pauses install-pack ./my_pack/
```

Validate before submitting:
```bash
active-pauses validate-pack ./my_pack/
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for dev environment setup, architecture overview, and how to add exercises and avatars.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgements & Research Sources

- **NIOSH** — National Institute for Occupational Safety and Health: [Computer Workstations eTool](https://www.cdc.gov/niosh/topics/ergonomics/)
- **EU-OSHA** — European Agency for Safety and Health at Work: [Work-related musculoskeletal disorders prevention](https://osha.europa.eu/en/themes/musculoskeletal-disorders)
- **Biswas et al. (2015)** — "Sedentary Time and Its Association with Risk for Disease Incidence, Mortality, and Hospitalization in Adults" — *Annals of Internal Medicine*
- **Stamatakis et al. (2019)** — "Sitting Time, Physical Activity, and Risk of Mortality in Adults" — *JAMA*
- **British Journal of Sports Medicine** — [Physical activity guidelines](https://bjsm.bmj.com/)
- **Pomodoro Technique** — Francesco Cirillo (1987)
- Avatar artwork by [Artist Name] — CC-BY 4.0
```

---

# SECTION 5: CONTRIBUTING.md (FULL DRAFT)

```markdown
# Contributing to active-pauses

Thank you for your interest in contributing. This guide covers everything you need to go from zero to a merged pull request on Ubuntu 24.04.

## Code of Conduct

This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be kind, constructive, and inclusive.

---

## Dev Environment Setup (Ubuntu 24.04, step by step)

### 1. System dependencies

```bash
sudo apt update
sudo apt install -y \
  python3.12 python3.12-venv python3.12-dev \
  python3-gi python3-gi-cairo gir1.2-gtk-4.0 \
  libgirepository1.0-dev libcairo2-dev pkg-config \
  libdbus-1-dev libsecret-1-dev \
  libnotify-dev \
  sqlite3 \
  git curl wget
```

### 2. Clone the repository

```bash
git clone https://github.com/yourusername/active-pauses.git
cd active-pauses
```

### 3. Create and activate a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 4. Install the package in editable mode with dev dependencies

```bash
pip install -e ".[dev]"
```

This installs the package plus: `pytest`, `pytest-asyncio`, `hypothesis`, `mypy`, `ruff`, `black`, `alembic`, and all runtime dependencies.

### 5. Set up the database

```bash
active-pauses db upgrade
```

This runs Alembic migrations against `~/.local/share/active-pauses/active-pauses.db`.

### 6. Run the daemon in dev mode (foreground, debug logging)

```bash
./scripts/run_daemon_dev.sh
# or:
active-pauses start --foreground --log-level debug
```

### 7. Run the test suite

```bash
pytest tests/ -v
```

Expected: all tests pass in < 30 seconds on first run.

### 8. Run linting and type checking

```bash
ruff check src/ tests/
black --check src/ tests/
mypy --strict src/
```

All three must pass before opening a PR.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    systemd user service                   │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │           active_pauses.daemon.main              │   │
│   │  asyncio event loop                              │   │
│   │                                                  │   │
│   │  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │   │
│   │  │scheduler │  │  ipc     │  │ config_watcher│  │   │
│   │  │(APSched) │  │(DBus)    │  │ (inotify)     │  │   │
│   │  └────┬─────┘  └────┬─────┘  └───────────────┘  │   │
│   │       │             │                             │   │
│   │  ┌────▼─────────────▼──────────────────────┐     │   │
│   │  │          notification.py                  │     │   │
│   │  │    (libnotify + action buttons)           │     │   │
│   │  └────────────────────┬─────────────────────┘     │   │
│   │                       │ "Do it now"                │   │
│   │  ┌────────────────────▼─────────────────────┐     │   │
│   │  │         window/exercise_window.py         │     │   │
│   │  │   GTK4 window + SVG avatar + CSS anim     │     │   │
│   │  └──────────────────────────────────────────┘     │   │
│   │                                                  │   │
│   │  ┌──────────────────────────────────────────┐    │   │
│   │  │          web/server.py                    │    │   │
│   │  │  FastAPI on 127.0.0.1:7331               │    │   │
│   │  └──────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
              │                       │
              ▼                       ▼
   ~/.config/active-pauses/    ~/.local/share/active-pauses/
   config.toml                 active-pauses.db
                                exercises/ (packs)
```

**Key data flows:**
1. `scheduler.py` fires a callback every N minutes per muscle group
2. Callback calls `exercises/selector.py` → picks an exercise respecting profile contraindications and recency
3. Calls `notification.py` → fires libnotify notification with action buttons
4. User clicks "Do it now" → notification action triggers DBus call → daemon spawns `window/exercise_window.py`
5. Exercise window composes avatar layers via `avatars/renderer.py`, plays CSS animation
6. On completion, logs to SQLite via `db/repositories/exercise_log_repo.py`
7. `web/server.py` (always running) serves live data to browser UI via FastAPI endpoints

---

## How to Add an Exercise

1. **Choose the correct TOML file** in `exercise_packs/builtin/exercises/[muscle_group].toml` (or create a new community pack)

2. **Copy the template** from `config_schema/exercise.schema.toml` and fill in all required fields

3. **Add a research source** — every exercise must have a `research_source` field. Use DOI format when possible: `"doi:10.1136/bjsports-2018-100078"` or a full NIOSH/EU-OSHA URL.

4. **Specify contraindications** accurately and conservatively. When in doubt, add the contraindication.

5. **Reference or create an animation**: Set `animation_ref = "muscle_group_exercise_slug"`. If the animation CSS doesn't exist yet, create `assets/animations/[ref].css` with keyframes and a `prefers-reduced-motion` fallback.

6. **Validate**: `active-pauses validate-pack exercise_packs/builtin/`

7. **Test manually**: `active-pauses trigger [your_exercise_id]` and watch the exercise window

8. **Write a unit test** in `tests/unit/test_exercise_loader.py` confirming your exercise loads and validates

9. **Open a PR** using the exercise pack template

---

## How to Add an Avatar Variant

See `assets/avatars/README.md` for the complete SVG authoring spec. Key points:

1. **viewBox must be `0 0 200 400`** — all base bodies use this canvas
2. **Use the standard layer IDs**: `layer-torso`, `layer-head`, `layer-left-arm`, `layer-right-arm`, `layer-left-leg`, `layer-right-leg`
3. **Skin tone naming**: `s1` = Fitzpatrick I-II, `s2` = III, `s3` = IV, `s4` = V, `s5` = VI
4. **Export from Inkscape**: File → Clean Up Document before saving; strip metadata
5. **Run snapshot tests** after adding: `pytest tests/snapshots/ -v --snapshot-update`
6. **Open a PR** using the avatar asset template

---

## How to Write Tests

### Unit tests
Test one function in isolation. Mock all I/O (filesystem, DBus, SQLite).

```python
# tests/unit/test_scheduler.py
def test_snooze_delays_all_timers(mock_scheduler: APScheduler) -> None:
    """Snoozeing shifts the next_run_time for every job by snooze_minutes."""
    scheduler = TimerScheduler(mock_scheduler)
    original_times = {job.id: job.next_run_time for job in mock_scheduler.get_jobs()}

    scheduler.snooze(minutes=10)

    for job in mock_scheduler.get_jobs():
        delta = job.next_run_time - original_times[job.id]
        assert delta == timedelta(minutes=10), f"Job {job.id} not delayed by 10m"
```

### Integration tests
Use `pytest-asyncio` and a real in-memory SQLite database. Test DBus with a subprocess-launched daemon fixture (see `tests/conftest.py`).

### Property-based tests (hypothesis)
Use `@given` for any scheduling or scoring logic with large input spaces:

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10))
def test_body_score_bounded(back_count: int, neck_count: int) -> None:
    score = calculate_body_score(back=back_count, neck=neck_count, ...)
    assert 0 <= score <= 100
```

---

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]

[optional footer: Closes #N]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

**Scopes:** `daemon`, `cli`, `web`, `exercises`, `avatars`, `db`, `gamification`, `analytics`, `plugins`, `packaging`

**Examples:**
```
feat(daemon): add fullscreen detection for X11 via python-xlib
fix(scheduler): snooze not applying to standing desk timer
docs(exercises): add back pain contraindication guidance
test(scheduler): add hypothesis tests for snooze boundary conditions
chore(deps): bump APScheduler from 3.10.1 to 3.10.4
```

---

## PR Process

1. **Fork** the repository and create a branch: `git checkout -b feat/daemon/your-feature`
2. **Write tests first** (TDD): write a failing test, then implement
3. **Ensure all checks pass** locally: `ruff`, `black`, `mypy`, `pytest`
4. **Open a PR** using the appropriate template from `.github/PULL_REQUEST_TEMPLATE/`
5. **Address review feedback** — maintainers aim to review within 3 business days
6. **Squash merge** is preferred for feature PRs; merge commits for release PRs

---

## Release Process

Releases are managed by maintainers:

1. Update `CHANGELOG.md`: move `[Unreleased]` items under a new version section
2. Bump version in `src/active_pauses/__init__.py` and `pyproject.toml`
3. Commit: `chore(release): bump version to 1.1.0`
4. Tag: `git tag -s v1.1.0 -m "Release v1.1.0"`
5. Push tag: `git push origin v1.1.0`
6. GitHub Actions `release.yml` automatically builds `.deb`, `.snap`, PyPI wheel, and creates the GitHub Release
```

---

# SECTION 6: EXERCISE LIBRARY SPECIFICATION

## 6.1 Data Model

All exercises are represented as `Exercise` Pydantic v2 models in `src/active_pauses/exercises/models.py`.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique slug, `[a-z0-9_]+`, globally unique across all packs |
| `name` | `str` | Human-readable name, ≤60 chars |
| `muscle_groups` | `list[MuscleGroup]` | ≥1 group from enum |
| `intensity` | `int` | 1=gentle, 2=moderate, 3=vigorous |
| `duration_seconds` | `int` | Total exercise duration, 10–300 |
| `rest_seconds` | `int` | Rest period after exercise, 0–60 |
| `animation_ref` | `str` | CSS animation identifier slug |
| `research_source` | `str` | Citation (DOI preferred) |
| `verbal_cue` | `str` | Primary instruction ≤120 chars (for audio/screen reader) |
| `phases` | `list[ExercisePhase]` | Ordered breathing/movement phases |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `hold_seconds` | `int \| None` | `None` | Per-rep hold time if applicable |
| `reps` | `int \| None` | `None` | Number of repetitions |
| `sets` | `int \| None` | `None` | Number of sets |
| `contraindications` | `list[str]` | `[]` | Condition slugs that exclude this exercise |
| `bilateral` | `bool` | `False` | True if exercise must be done on both sides |
| `equipment` | `list[str]` | `[]` | Required equipment (empty = no equipment) |
| `notes` | `str \| None` | `None` | Free-text notes ≤500 chars |
| `tags` | `list[str]` | `[]` | Arbitrary tags for filtering |

### `MuscleGroup` Enum

```python
class MuscleGroup(str, Enum):
    BACK = "back"
    NECK = "neck"
    WRISTS = "wrists"
    EYES = "eyes"
    LEGS = "legs"
    FULLBODY = "fullbody"
    SHOULDERS = "shoulders"
    HIPS = "hips"
```

### `ExercisePhase` Model

```python
class ExercisePhase(BaseModel):
    name: Literal["inhale", "exhale", "hold", "move", "rest"]
    duration_seconds: int  # 1–60
    cue: str               # ≤120 chars, read aloud / shown in window
```

### Contraindication Slugs (canonical list)

```
spinal_surgery          recent_back_injury       herniated_disc_acute
herniated_disc_chronic  neck_surgery             carpal_tunnel_severe
carpal_tunnel_mild      pregnancy_first_trimester  pregnancy_any
glaucoma                retinal_detachment       knee_replacement
knee_injury_acute       hip_replacement          osteoporosis_severe
hypertension_severe     vertigo                  shoulder_surgery
wrist_fracture_healing  postpartum_4weeks        epilepsy
```

---

## 6.2 TOML Schema (exercise.schema.toml — annotated)

```toml
# Each exercise is an [[exercise]] array element.
# All required fields must be present. Validation runs via pydantic on load.

[[exercise]]
# REQUIRED: unique slug [a-z0-9_]+, globally unique across all packs
id = "back_cat_cow"

# REQUIRED: human-readable name (≤60 chars)
name = "Cat-Cow Stretch"

# REQUIRED: list of muscle groups from MuscleGroup enum
muscle_groups = ["back", "neck"]

# REQUIRED: 1=gentle, 2=moderate, 3=vigorous
intensity = 1

# REQUIRED: total duration in seconds (10–300)
duration_seconds = 60

# REQUIRED: rest period after exercise in seconds (0–60)
rest_seconds = 10

# REQUIRED: matches CSS animation slug in assets/animations/
animation_ref = "back_cat_cow"

# REQUIRED: research source (DOI preferred, or full URL)
research_source = "doi:10.1097/00007632-199706150-00011"

# REQUIRED: primary verbal instruction ≤120 chars
verbal_cue = "On hands and knees, arch your back up like a cat, then dip it down like a cow"

# OPTIONAL: per-rep hold time in seconds
hold_seconds = 3

# OPTIONAL: number of reps
reps = 10

# OPTIONAL: contraindication slugs — exercise hidden for matching profiles
contraindications = ["spinal_surgery", "herniated_disc_acute"]

# OPTIONAL: true if must be done on both sides (exercise window will cue both sides)
bilateral = false

# REQUIRED: at least one phase
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Breathe in as you arch your back downward (Cow)"

[[exercise.phases]]
name = "exhale"
duration_seconds = 3
cue = "Breathe out as you round your back upward (Cat)"

[[exercise.phases]]
name = "hold"
duration_seconds = 2
cue = "Hold the cat position"
```

---

## 6.3 Seed Exercises (20 exercises)

### Back Group (4 exercises)

**1. Cat-Cow Stretch**
```toml
[[exercise]]
id = "back_cat_cow"
name = "Cat-Cow Stretch"
muscle_groups = ["back", "neck"]
intensity = 1
duration_seconds = 60
rest_seconds = 10
reps = 10
hold_seconds = 2
contraindications = ["spinal_surgery", "herniated_disc_acute"]
animation_ref = "back_cat_cow"
research_source = "doi:10.1097/00007632-199706150-00011"
verbal_cue = "On hands and knees, arch your back up like a cat, then dip it down like a cow"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Breathe in — drop belly down, lift head (Cow)"
[[exercise.phases]]
name = "exhale"
duration_seconds = 3
cue = "Breathe out — round spine up, tuck chin (Cat)"
```

**2. Seated Forward Fold**
```toml
[[exercise]]
id = "back_seated_forward_fold"
name = "Seated Forward Fold"
muscle_groups = ["back", "legs"]
intensity = 1
duration_seconds = 45
rest_seconds = 10
hold_seconds = 20
bilateral = false
contraindications = ["herniated_disc_acute", "spinal_surgery"]
animation_ref = "back_seated_forward_fold"
research_source = "https://www.cdc.gov/niosh/topics/ergonomics/"
verbal_cue = "Sit at edge of chair, hinge forward from hips, let arms hang toward floor"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Sit tall, breathe in"
[[exercise.phases]]
name = "exhale"
duration_seconds = 5
cue = "Hinge forward slowly as you exhale"
[[exercise.phases]]
name = "hold"
duration_seconds = 20
cue = "Breathe naturally, feel the stretch along your spine"
[[exercise.phases]]
name = "inhale"
duration_seconds = 4
cue = "Slowly roll back up, stacking vertebrae"
```

**3. Thoracic Extension (Chair Back)**
```toml
[[exercise]]
id = "back_thoracic_extension"
name = "Thoracic Extension Over Chair"
muscle_groups = ["back", "shoulders"]
intensity = 1
duration_seconds = 40
rest_seconds = 10
hold_seconds = 15
contraindications = ["spinal_surgery", "osteoporosis_severe", "herniated_disc_acute"]
animation_ref = "back_thoracic_extension"
research_source = "doi:10.1016/j.jmpt.2009.08.012"
verbal_cue = "Clasp hands behind head, lean back gently over the top of your chair back"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Sit upright, hands clasped behind head"
[[exercise.phases]]
name = "exhale"
duration_seconds = 5
cue = "Lean gently back over the chair top"
[[exercise.phases]]
name = "hold"
duration_seconds = 15
cue = "Breathe naturally, feel upper back opening"
[[exercise.phases]]
name = "move"
duration_seconds = 5
cue = "Slowly return to upright"
```

**4. Seated Spinal Twist**
```toml
[[exercise]]
id = "back_seated_spinal_twist"
name = "Seated Spinal Twist"
muscle_groups = ["back", "neck"]
intensity = 1
duration_seconds = 50
rest_seconds = 10
hold_seconds = 15
bilateral = true
contraindications = ["spinal_surgery", "herniated_disc_acute"]
animation_ref = "back_seated_spinal_twist"
research_source = "https://osha.europa.eu/en/publications/e-facts/efact72"
verbal_cue = "Sit tall, place right hand on left knee, gently rotate left from the waist"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Breathe in, sit tall"
[[exercise.phases]]
name = "exhale"
duration_seconds = 5
cue = "Rotate gently to the left as you exhale"
[[exercise.phases]]
name = "hold"
duration_seconds = 15
cue = "Breathe naturally in the twist"
[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Release back to center"
[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Repeat on the right side"
```

### Neck Group (4 exercises)

**5. Neck Side Tilt**
```toml
[[exercise]]
id = "neck_side_tilt"
name = "Neck Side Tilt"
muscle_groups = ["neck"]
intensity = 1
duration_seconds = 45
rest_seconds = 10
hold_seconds = 15
bilateral = true
contraindications = ["neck_surgery", "vertigo"]
animation_ref = "neck_side_tilt"
research_source = "https://www.cdc.gov/niosh/topics/ergonomics/"
verbal_cue = "Slowly tilt your right ear toward your right shoulder, hold, then switch sides"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Breathe in, sit tall"
[[exercise.phases]]
name = "exhale"
duration_seconds = 3
cue = "Gently tilt right ear to right shoulder"
[[exercise.phases]]
name = "hold"
duration_seconds = 15
cue = "Hold — feel the left side of your neck stretching"
[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Return to center, then repeat left"
```

**6. Chin Tucks**
```toml
[[exercise]]
id = "neck_chin_tucks"
name = "Chin Tucks"
muscle_groups = ["neck"]
intensity = 1
duration_seconds = 40
rest_seconds = 10
reps = 10
contraindications = ["neck_surgery"]
animation_ref = "neck_chin_tucks"
research_source = "doi:10.1177/0363546503258714"
verbal_cue = "Gently pull your chin straight back, making a double chin — hold 3 seconds, repeat"
[[exercise.phases]]
name = "move"
duration_seconds = 2
cue = "Draw chin straight back"
[[exercise.phases]]
name = "hold"
duration_seconds = 3
cue = "Hold — feel the back of your neck lengthen"
[[exercise.phases]]
name = "move"
duration_seconds = 2
cue = "Release forward"
```

**7. Neck Circles (Half)**
```toml
[[exercise]]
id = "neck_half_circles"
name = "Neck Half Circles"
muscle_groups = ["neck"]
intensity = 1
duration_seconds = 45
rest_seconds = 10
reps = 5
contraindications = ["neck_surgery", "vertigo", "herniated_disc_acute"]
animation_ref = "neck_half_circles"
research_source = "https://osha.europa.eu/en/publications/e-facts/efact72"
verbal_cue = "Slowly roll your head from right shoulder, down through chin to chest, to left shoulder — no full back circles"
[[exercise.phases]]
name = "exhale"
duration_seconds = 5
cue = "Roll head from right to center (chin to chest)"
[[exercise.phases]]
name = "inhale"
duration_seconds = 5
cue = "Roll head from center to left shoulder"
```

**8. Upper Trapezius Stretch**
```toml
[[exercise]]
id = "neck_upper_trap_stretch"
name = "Upper Trapezius Stretch"
muscle_groups = ["neck", "shoulders"]
intensity = 1
duration_seconds = 50
rest_seconds = 10
hold_seconds = 20
bilateral = true
contraindications = ["neck_surgery", "shoulder_surgery"]
animation_ref = "neck_upper_trap_stretch"
research_source = "doi:10.1186/1471-2474-12-176"
verbal_cue = "Hold chair seat with right hand, tilt left ear to left shoulder, use left hand to gently deepen stretch"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Anchor right hand under chair seat"
[[exercise.phases]]
name = "exhale"
duration_seconds = 5
cue = "Tilt left ear toward left shoulder"
[[exercise.phases]]
name = "hold"
duration_seconds = 20
cue = "Breathe naturally — feel right trap releasing"
[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Slowly return, switch sides"
```

### Wrists Group (3 exercises)

**9. Wrist Circles**
```toml
[[exercise]]
id = "wrists_circles"
name = "Wrist Circles"
muscle_groups = ["wrists"]
intensity = 1
duration_seconds = 30
rest_seconds = 5
reps = 10
bilateral = true
contraindications = ["wrist_fracture_healing", "carpal_tunnel_severe"]
animation_ref = "wrists_circles"
research_source = "https://www.cdc.gov/niosh/topics/ergonomics/"
verbal_cue = "Interlace fingers, rotate wrists in full circles — 10 times each direction"
[[exercise.phases]]
name = "move"
duration_seconds = 10
cue = "Rotate wrists clockwise — 10 slow circles"
[[exercise.phases]]
name = "move"
duration_seconds = 10
cue = "Rotate wrists counterclockwise — 10 slow circles"
```

**10. Prayer Stretch**
```toml
[[exercise]]
id = "wrists_prayer_stretch"
name = "Prayer Stretch"
muscle_groups = ["wrists"]
intensity = 1
duration_seconds = 40
rest_seconds = 10
hold_seconds = 15
contraindications = ["wrist_fracture_healing", "carpal_tunnel_severe"]
animation_ref = "wrists_prayer_stretch"
research_source = "doi:10.1016/j.jhsa.2003.08.004"
verbal_cue = "Press palms together in front of chest, slowly lower hands while keeping palms pressed — feel stretch in wrist extensors"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Press palms together at chest height"
[[exercise.phases]]
name = "exhale"
duration_seconds = 5
cue = "Slowly lower palms toward waist — hold at first stretch"
[[exercise.phases]]
name = "hold"
duration_seconds = 15
cue = "Breathe naturally — feel the stretch in your wrist extensors"
```

**11. Finger Spreads**
```toml
[[exercise]]
id = "wrists_finger_spreads"
name = "Finger Spreads"
muscle_groups = ["wrists"]
intensity = 1
duration_seconds = 30
rest_seconds = 5
reps = 10
contraindications = ["wrist_fracture_healing"]
animation_ref = "wrists_finger_spreads"
research_source = "https://www.cdc.gov/niosh/topics/ergonomics/"
verbal_cue = "Spread fingers wide apart, hold 2 seconds, then make a gentle fist — repeat 10 times"
[[exercise.phases]]
name = "move"
duration_seconds = 2
cue = "Spread fingers as wide as possible"
[[exercise.phases]]
name = "hold"
duration_seconds = 2
cue = "Hold spread"
[[exercise.phases]]
name = "move"
duration_seconds = 2
cue = "Gently curl into a loose fist"
```

### Eyes Group (3 exercises)

**12. 20-20-20 Rule**
```toml
[[exercise]]
id = "eyes_20_20_20"
name = "20-20-20 Eye Break"
muscle_groups = ["eyes"]
intensity = 1
duration_seconds = 25
rest_seconds = 5
contraindications = []
animation_ref = "eyes_20_20_20"
research_source = "doi:10.1097/OPX.0b013e3182934a85"
verbal_cue = "Look at an object at least 20 feet away for 20 seconds — let your eye muscles fully relax"
[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Find a point at least 6 meters (20 feet) away"
[[exercise.phases]]
name = "hold"
duration_seconds = 20
cue = "Gaze softly — blink naturally — relax"
```

**13. Eye Palming**
```toml
[[exercise]]
id = "eyes_palming"
name = "Eye Palming"
muscle_groups = ["eyes"]
intensity = 1
duration_seconds = 60
rest_seconds = 5
contraindications = ["glaucoma", "retinal_detachment"]
animation_ref = "eyes_palming"
research_source = "https://www.cdc.gov/niosh/topics/ergonomics/"
verbal_cue = "Rub palms together to warm them, gently cup over closed eyes without pressure"
[[exercise.phases]]
name = "move"
duration_seconds = 5
cue = "Rub palms briskly to generate warmth"
[[exercise.phases]]
name = "hold"
duration_seconds = 50
cue = "Cup warm palms gently over closed eyes — breathe deeply — see only darkness"
```

**14. Eye Tracking (Figure 8)**
```toml
[[exercise]]
id = "eyes_figure_8"
name = "Eye Figure-8 Tracking"
muscle_groups = ["eyes"]
intensity = 1
duration_seconds = 30
rest_seconds = 5
reps = 4
contraindications = ["retinal_detachment", "glaucoma"]
animation_ref = "eyes_figure_8"
research_source = "doi:10.1097/OPX.0b013e3182934a85"
verbal_cue = "Imagine a figure 8 on its side in front of you — trace it slowly with your eyes, 2 times each direction"
[[exercise.phases]]
name = "move"
duration_seconds = 8
cue = "Trace the figure-8 clockwise — slow and smooth"
[[exercise.phases]]
name = "move"
duration_seconds = 8
cue = "Trace the figure-8 counterclockwise"
```

### Legs Group (3 exercises)

**15. Seated Leg Extensions**
```toml
[[exercise]]
id = "legs_seated_extensions"
name = "Seated Leg Extensions"
muscle_groups = ["legs"]
intensity = 1
duration_seconds = 45
rest_seconds = 10
reps = 10
bilateral = true
contraindications = ["knee_replacement", "knee_injury_acute"]
animation_ref = "legs_seated_extensions"
research_source = "https://osha.europa.eu/en/publications/e-facts/efact72"
verbal_cue = "Sitting upright, slowly extend right leg until parallel with floor, hold 3 seconds, lower. Repeat left."
[[exercise.phases]]
name = "inhale"
duration_seconds = 2
cue = "Breathe in — sit tall"
[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Slowly extend right leg to horizontal"
[[exercise.phases]]
name = "hold"
duration_seconds = 3
cue = "Hold — squeeze quad gently"
[[exercise.phases]]
name = "exhale"
duration_seconds = 3
cue = "Lower slowly as you exhale"
```

**16. Calf Raises (Seated)**
```toml
[[exercise]]
id = "legs_calf_raises_seated"
name = "Seated Calf Raises"
muscle_groups = ["legs"]
intensity = 1
duration_seconds = 30
rest_seconds = 10
reps = 15
contraindications = ["knee_injury_acute"]
animation_ref = "legs_calf_raises_seated"
research_source = "doi:10.1136/bjsports-2018-100078"
verbal_cue = "Feet flat on floor — raise heels as high as possible, pause at top, lower slowly"
[[exercise.phases]]
name = "move"
duration_seconds = 1
cue = "Raise heels — press through the balls of your feet"
[[exercise.phases]]
name = "hold"
duration_seconds = 1
cue = "Hold at the top"
[[exercise.phases]]
name = "move"
duration_seconds = 1
cue = "Lower heels slowly"
```

**17. Hip Flexor Stretch (Standing)**
```toml
[[exercise]]
id = "legs_hip_flexor_standing"
name = "Standing Hip Flexor Stretch"
muscle_groups = ["legs", "hips"]
intensity = 1
duration_seconds = 60
rest_seconds = 10
hold_seconds = 20
bilateral = true
contraindications = ["hip_replacement", "knee_injury_acute", "knee_replacement"]
animation_ref = "legs_hip_flexor_standing"
research_source = "doi:10.1136/bjsports-2018-100078"
verbal_cue = "Step one foot forward into a lunge, keep back knee straight — feel hip flexor of back leg stretching"
notes = "Hold chair or desk for balance if needed"
[[exercise.phases]]
name = "move"
duration_seconds = 5
cue = "Step right foot forward, keep torso upright"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Breathe in — lengthen spine"
[[exercise.phases]]
name = "hold"
duration_seconds = 20
cue = "Breathe naturally — feel left hip flexor releasing"
[[exercise.phases]]
name = "move"
duration_seconds = 5
cue = "Step back, switch legs"
```

### Full Body Group (3 exercises)

**18. Standing Overhead Reach**
```toml
[[exercise]]
id = "fullbody_overhead_reach"
name = "Standing Overhead Reach"
muscle_groups = ["fullbody", "back", "shoulders"]
intensity = 1
duration_seconds = 40
rest_seconds = 10
reps = 5
bilateral = true
contraindications = ["shoulder_surgery", "spinal_surgery"]
animation_ref = "fullbody_overhead_reach"
research_source = "https://osha.europa.eu/en/publications/e-facts/efact72"
verbal_cue = "Stand tall, reach both arms overhead, then reach right arm higher, then left — alternate 5 times each side"
[[exercise.phases]]
name = "inhale"
duration_seconds = 3
cue = "Rise onto tiptoes, reach both arms up"
[[exercise.phases]]
name = "exhale"
duration_seconds = 3
cue = "Reach right arm higher — feel the side body lengthen"
[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Switch — reach left arm higher"
```

**19. Desk Pushup**
```toml
[[exercise]]
id = "fullbody_desk_pushup"
name = "Desk Push-Up"
muscle_groups = ["fullbody", "shoulders"]
intensity = 2
duration_seconds = 45
rest_seconds = 15
reps = 10
sets = 1
contraindications = ["shoulder_surgery", "wrist_fracture_healing", "carpal_tunnel_severe"]
animation_ref = "fullbody_desk_pushup"
research_source = "doi:10.1136/bjsports-2018-100078"
verbal_cue = "Hands on desk edge, shoulder-width apart, lower chest to desk, push back up — keep body in a plank line"
[[exercise.phases]]
name = "inhale"
duration_seconds = 2
cue = "Breathe in — lower chest toward desk"
[[exercise.phases]]
name = "exhale"
duration_seconds = 2
cue = "Breathe out — push back to start"
```

**20. Chair Squats**
```toml
[[exercise]]
id = "fullbody_chair_squats"
name = "Chair Squats (Sit to Stand)"
muscle_groups = ["fullbody", "legs", "hips"]
intensity = 2
duration_seconds = 50
rest_seconds = 15
reps = 10
contraindications = ["hip_replacement", "knee_replacement", "knee_injury_acute"]
animation_ref = "fullbody_chair_squats"
research_source = "doi:10.1136/bjsports-2018-100078"
verbal_cue = "Stand from chair slowly without using hands, lower back down under control — engage your glutes at the top"
[[exercise.phases]]
name = "inhale"
duration_seconds = 2
cue = "Breathe in — lean slightly forward from hips"
[[exercise.phases]]
name = "move"
duration_seconds = 2
cue = "Press through heels — stand up fully"
[[exercise.phases]]
name = "exhale"
duration_seconds = 2
cue = "Breathe out — slowly lower back to hover above chair"
```

---

# SECTION 7: AVATAR SYSTEM SPECIFICATION

## 7.1 SVG Modular Layer Architecture

Each avatar display is a composite of 4 ordered SVG layers, stacked using CSS `position: absolute` within a fixed `200×400` viewport:

```
Layer Stack (top to bottom rendering order):
┌─────────────────────────────────┐ z-index: 4
│     Face & Hair Layer            │  face_{variant}.svg
├─────────────────────────────────┤ z-index: 3
│     Clothing Layer               │  clothing_{style}.svg
├─────────────────────────────────┤ z-index: 2
│   Muscle Highlight Overlay       │  highlight_{muscle_group}.svg
│   (semi-transparent, animated)   │
├─────────────────────────────────┤ z-index: 1
│     Base Body Layer              │  body_{expr}_{skin}.svg
└─────────────────────────────────┘
```

### Layer 1: Base Body SVG

**File naming:** `body_{expr}_s{n}.svg`
- `expr` ∈ `{masc, femm, nbin}`
- `n` ∈ `{1, 2, 3, 4, 5}` (Fitzpatrick scale groups)

**SVG structure — required element IDs:**
```xml
<svg id="avatar-base" viewBox="0 0 200 400" xmlns="http://www.w3.org/2000/svg">
  <g id="layer-legs">      <!-- Both legs -->
    <path id="layer-left-leg"  .../>
    <path id="layer-right-leg" .../>
  </g>
  <g id="layer-torso">     <!-- Torso/trunk -->
    <path id="layer-spine-area" .../>  <!-- Used by highlight overlay anchor -->
  </g>
  <g id="layer-arms">
    <path id="layer-left-arm"  .../>
    <path id="layer-right-arm" .../>
  </g>
  <g id="layer-head">
    <path id="layer-neck"  .../>       <!-- Used by neck highlight anchor -->
    <path id="layer-skull" .../>
  </g>
  <!-- Hands: always included in base, wrist overlay references these -->
  <g id="layer-hands">
    <path id="layer-left-hand"  .../>
    <path id="layer-right-hand" .../>
  </g>
</svg>
```

**Skin tone color variables (CSS custom properties in base SVG):**
```css
/* Defined per skin tone file; used throughout the SVG paths */
:root {
  --skin-primary: #F5CBA7;    /* s1: Fitzpatrick I-II */
  --skin-shadow: #E8B48A;
  --skin-highlight: #FDEBD0;
}
/* s2: --skin-primary: #DEB887; --skin-shadow: #C8A07A; --skin-highlight: #EED5A8 */
/* s3: --skin-primary: #C68642; --skin-shadow: #A0692F; --skin-highlight: #D4975A */
/* s4: --skin-primary: #8D5524; --skin-shadow: #6B3E18; --skin-highlight: #A06730 */
/* s5: --skin-primary: #4A2912; --skin-shadow: #32180A; --skin-highlight: #5C3520 */
```

### Layer 2: Muscle Highlight Overlay SVG

**File naming:** `highlight_{muscle_group}.svg`

**Design rules:**
- viewBox matches base: `0 0 200 400`
- Use `fill-opacity: 0.35` on highlight paths — semi-transparent pulsing glow
- Color: `#FF6B35` (warm orange) pulsing via CSS `@keyframes pulse-highlight`
- Paths trace the exact muscle group region on the body (aligned to base body coordinates)
- The overlay SVG is transparent everywhere except the highlighted region
- `aria-hidden="true"` on overlay (screen reader sees verbal cue text, not SVG)

**Example `highlight_wrists.svg` (abridged):**
```xml
<svg viewBox="0 0 200 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <style>
    .muscle-highlight {
      fill: #FF6B35;
      fill-opacity: 0.35;
      animation: pulse-highlight 1.5s ease-in-out infinite;
    }
    @keyframes pulse-highlight {
      0%, 100% { fill-opacity: 0.2; }
      50%       { fill-opacity: 0.6; }
    }
    @media (prefers-reduced-motion: reduce) {
      .muscle-highlight { animation: none; fill-opacity: 0.4; }
    }
  </style>
  <!-- Wrist region — coordinates match base body wrist paths -->
  <ellipse class="muscle-highlight" cx="42" cy="285" rx="12" ry="8"/>  <!-- left wrist -->
  <ellipse class="muscle-highlight" cx="158" cy="285" rx="12" ry="8"/> <!-- right wrist -->
</svg>
```

### Layer 3: Clothing Layer SVG

**File naming:** `clothing_{style}.svg`
- `style` ∈ `{casual_default, office_default}`
- viewBox: `0 0 200 400`
- Clothing paths cover only the clothed body regions (chest, arms partially, legs from waist)
- Must have `id="clothing-layer"` on the root `<g>` for runtime show/hide

### Layer 4: Face & Hair Layer SVG

**File naming:** `face_{variant}.svg` — `variant` ∈ `{a, b, c}`
- viewBox: `0 0 200 400` (face positioned in upper region ~y:20-120)
- Includes: eyes (id: `face-eyes`), mouth (id: `face-mouth`), hair (id: `face-hair`)
- Expression state: `data-expression` attribute on root SVG, values: `neutral`, `happy`, `focused`
  - `neutral` = default resting pose
  - `focused` = eyes slightly narrowed (exercise in progress)
  - `happy` = smile (exercise complete)

---

## 7.2 Animation: CSS Keyframe Architecture

Each exercise has a corresponding CSS file in `assets/animations/`:

**File naming:** `{muscle_group}_{exercise_slug}.css`

**CSS class naming convention:**
- Animation CSS class: `anim-{exercise_id}` — applied to the base body SVG element
- Keyframe names: `kf-{exercise_id}-{phase}` e.g. `kf-back-cat-cow-arch`

**Keyframe rules — ONLY use transform/opacity (no layout-triggering properties):**
```css
/* assets/animations/back_cat_cow.css */

@keyframes kf-back-cat-cow-arch {
  0%   { transform: translateY(0) scaleY(1); }
  50%  { transform: translateY(-4px) scaleY(0.97); }
  100% { transform: translateY(0) scaleY(1); }
}

@keyframes kf-back-cat-cow-round {
  0%   { transform: translateY(0) scaleY(1); }
  50%  { transform: translateY(4px) scaleY(1.03); }
  100% { transform: translateY(0) scaleY(1); }
}

.anim-back-cat-cow #layer-torso {
  animation: kf-back-cat-cow-arch 6s ease-in-out infinite alternate;
  transform-origin: center center;
}

/* Reduced motion: static representative pose, no animation */
@media (prefers-reduced-motion: reduce) {
  .anim-back-cat-cow #layer-torso {
    animation: none;
    transform: translateY(-2px) scaleY(0.98);  /* hold mid-arch static pose */
  }
}
```

**How the exercise window applies the animation:**
1. `avatars/renderer.py` composes the 4 SVG layers into a single `<div class="avatar-container anim-{exercise_id}">`
2. The animation CSS file for that exercise is loaded into the GTK4 WebKit2 widget CSS provider
3. On exercise complete, class is removed; avatar returns to neutral pose

---

## 7.3 Rendering Pipeline

`avatars/renderer.py` exposes:

```python
def compose_avatar_html(
    profile: UserProfile,
    exercise: Exercise,
) -> str:
    """Return self-contained HTML string for the avatar composite.
    
    Loads base body SVG (by gender_expr + skin_tone from profile),
    muscle highlight overlay (from exercise.muscle_groups[0]),
    clothing layer (from profile.clothing_style),
    face/hair layer (from profile.face_variant),
    and the exercise animation CSS.
    Returns an HTML <div> wrapping 4 stacked <img> tags (SVG sources)
    with the animation CSS <style> block inline.
    Includes aria-label on the container and aria-hidden on all SVG layers.
    """
```

**GTK4 integration:** `window/exercise_window.py` uses a `Gtk.WebView` (WebKit2Gtk) widget to render the composed HTML. This avoids reimplementing SVG compositing in GTK directly and reuses the animation CSS without modification.

---

## 7.4 Accessibility: Reduced-Motion Mode

When `config.reduced_motion = true` OR the system-level `prefers-reduced-motion: reduce` media query is set:

1. **SVG animations:** All `animation:` declarations are overridden to `animation: none` via the `@media (prefers-reduced-motion: reduce)` block in each animation CSS file. A static representative pose (held mid-movement transform) is shown instead.
2. **Muscle highlight overlay:** The `pulse-highlight` keyframe animation is replaced with a static `fill-opacity: 0.4` (no pulsing).
3. **GTK4 window:** The exercise window adds CSS class `reduced-motion` to the WebView container, which triggers the reduced-motion styles.
4. **Audio cues:** Phase cues (`inhale.ogg`, `exhale.ogg`, `hold.ogg`) are still played unless `audio_cues = false`.
5. **Screen reader:** The `verbal_cue` text and all `ExercisePhase.cue` text are exposed via `aria-live="polite"` in the exercise window, cycling through phases as timers advance.

---

## 7.5 Avatar Selection Logic

```python
# avatars/models.py
@dataclass
class AvatarConfig:
    gender_expr: Literal["masc", "femm", "nbin"]  # from profile
    skin_tone: Literal["s1", "s2", "s3", "s4", "s5"]  # from profile
    face_variant: Literal["a", "b", "c"]             # from profile
    clothing_style: Literal["casual_default", "office_default"]  # from profile

def base_body_path(cfg: AvatarConfig) -> Path:
    return ASSETS_DIR / "avatars" / "base" / f"body_{cfg.gender_expr}_{cfg.skin_tone}.svg"

def highlight_path(exercise: Exercise) -> Path:
    # Use first muscle group as primary highlight
    group = exercise.muscle_groups[0].value
    return ASSETS_DIR / "avatars" / "overlays" / f"highlight_{group}.svg"
```

---

# SECTION 8: LOCAL WEB UI SPECIFICATION

The web UI is a Single Page Application served at `http://127.0.0.1:7331`. It uses Alpine.js 3.x for reactivity (vendored, no CDN), vanilla CSS, and Chart.js 4.x (vendored). No build step required. All pages are sections within `static/index.html`, toggled by Alpine.js router state.

---

## Page 1: Dashboard

**Route:** `#dashboard` (default)

**Purpose:** At-a-glance health summary and day control.

### Interactive Elements

| Element | Action | Data |
|---------|--------|------|
| Streak counter badge | Display only | `GET /api/gamification` → `streak_days` |
| Body score ring (Chart.js doughnut) | Display only | `GET /api/gamification` → `body_score` |
| "Today's exercises" progress bar | Display only | `GET /api/dashboard` → `completed_today`, `goal_today` |
| Next scheduled pause card (per muscle group) | Display only | `GET /api/dashboard` → `next_pauses[]` |
| "Snooze all 15m" button | POST → snooze | `POST /api/timers/snooze` body: `{"minutes": 15}` |
| "Pause daemon" toggle | POST → pause/resume | `POST /api/daemon/pause` or `POST /api/daemon/resume` |
| "Trigger exercise now" dropdown | POST → trigger | `POST /api/exercises/trigger` body: `{"exercise_id": "..."}` |
| Standing mode toggle | Toggle + POST | `PUT /api/standing` body: `{"standing": true}` |
| Calendar events for today | Display only | `GET /api/calendar/today` |

**API endpoints backing this page:**
- `GET /api/dashboard`
- `GET /api/gamification`
- `GET /api/calendar/today`
- `POST /api/timers/snooze`
- `POST /api/daemon/pause`
- `POST /api/daemon/resume`
- `POST /api/exercises/trigger`
- `PUT /api/standing`

---

## Page 2: Timer Configuration

**Route:** `#timers`

**Purpose:** Set interval, duration, and active hours per muscle group.

### Interactive Elements

| Element | Action | Data |
|---------|--------|------|
| Interval slider per muscle group (6 groups) | onChange → PUT | `PUT /api/timers` per group |
| Exercise duration input (seconds) | onChange → PUT | `PUT /api/timers` |
| Active hours range picker (start_hour, end_hour) | onChange → PUT | `PUT /api/timers` |
| Weekday checkboxes (Mon–Sun) | onChange → PUT | `PUT /api/timers` |
| "Pause on fullscreen" toggle | onChange → PUT | `PUT /api/timers` |
| "Pomodoro mode" toggle | onChange → PUT | `PUT /api/timers` |
| Reset to defaults button | POST → reset | `POST /api/timers/reset` |

**API endpoints:**
- `GET /api/timers`
- `PUT /api/timers`
- `POST /api/timers/reset`

---

## Page 3: Profile Setup / Onboarding

**Route:** `#profile`

**Onboarding flow (shown only on first launch):**

**Question 1:** "How would you describe your main activity at work?"
- Options: Typing-heavy (programmer/writer), Mixed keyboard/mouse, Phone calls & meetings, Creative (drawing/design)
- Maps to: `profile.type` and `wrists_interval_minutes` default

**Question 2:** "Do you have any of the following conditions?"
- Multi-select: Lower back issues, Neck/shoulder pain, Wrist/hand pain (carpal tunnel), Knee problems, Eye strain, None of the above
- Maps to: `profile.contraindications[]`

**Question 3:** "How would you describe your current fitness level?"
- Options: Prefer gentle stretches only, Comfortable with moderate movement, Happy with vigorous breaks
- Maps to: `profile.intensity_cap` (1, 2, or 3)

**Question 4:** "Do you use a standing desk?"
- Yes/No → sets `standing_desk.enabled`

**Question 5:** "How do you identify?" (for avatar selection)
- Masculine / Feminine / Non-binary / Prefer not to say
- Maps to: `profile.gender_expr`
- Immediately followed by skin tone selector (5 swatches)

### Interactive Elements (Edit Profile)

| Element | Action | Data |
|---------|--------|------|
| Profile type dropdown | onChange → PUT | `PUT /api/profile` → `profile_type` |
| Contraindications multi-select | onChange → PUT | `PUT /api/profile` → `contraindications[]` |
| Intensity cap slider (1–3) | onChange → PUT | `PUT /api/profile` → `intensity_cap` |
| Avatar gender expression selector | onChange → PUT | `PUT /api/profile` → `gender_expr` |
| Skin tone swatches (5 options) | onChange → PUT | `PUT /api/profile` → `skin_tone` |
| Face variant selector (3 options) | onChange → PUT | `PUT /api/profile` → `face_variant` |
| Reduced motion toggle | onChange → PUT | `PUT /api/profile` → `reduced_motion` |
| Audio cues toggle | onChange → PUT | `PUT /api/profile` → `audio_cues` |
| Re-run onboarding button | onClick → navigate | Client-side: show onboarding flow again |

**API endpoints:**
- `GET /api/profile`
- `PUT /api/profile`
- `POST /api/profile/onboarding`

---

## Page 4: Exercise Library Browser

**Route:** `#exercises`

**Interactive Elements:**

| Element | Action | Data |
|---------|--------|------|
| Muscle group filter tabs (7 options) | onClick → filter | `GET /api/exercises?muscle_group=back` |
| Intensity filter (1/2/3 checkboxes) | onChange → filter | `GET /api/exercises?intensity=1,2` |
| Contraindication filter toggle | onChange → filter | `GET /api/exercises?exclude_contraindications=true` (uses profile) |
| Search input | onChange → filter | `GET /api/exercises?q=neck` |
| Exercise card (expand) | onClick → show detail | `GET /api/exercises/{id}` |
| "Trigger now" button on each card | onClick → POST | `POST /api/exercises/trigger` body: `{"exercise_id": "..."}` |
| Pack source badge | Display only | From `GET /api/exercises` → `pack_id` field |

**API endpoints:**
- `GET /api/exercises`
- `GET /api/exercises/{id}`
- `POST /api/exercises/trigger`

---

## Page 5: Standing Desk Settings

**Route:** `#standing`

**Interactive Elements:**

| Element | Action | Data |
|---------|--------|------|
| Enable standing desk toggle | onChange → PUT | `PUT /api/standing` → `enabled` |
| Sit:Stand ratio dropdown (1:1, 2:1, 3:2) | onChange → PUT | `PUT /api/standing` → `ratio` |
| Max continuous standing alert (minutes) | onChange → PUT | `PUT /api/standing` → `max_standing_minutes` |
| Current posture indicator (live) | Display only | `GET /api/standing/current` (polls every 30s) |
| Today's sit/stand timeline chart | Display only | `GET /api/standing/today` → Chart.js timeline |

**API endpoints:**
- `GET /api/standing`
- `PUT /api/standing`
- `GET /api/standing/current`
- `GET /api/standing/today`

---

## Page 6: Gamification & Team Board

**Route:** `#gamification`

**Interactive Elements:**

| Element | Action | Data |
|---------|--------|------|
| Streak display (flame + count) | Display only | `GET /api/gamification` → `streak_days` |
| Body score ring chart | Display only | `GET /api/gamification` → `body_score`, `muscle_coverage{}` |
| Badge grid (15 badges) | Display only | `GET /api/gamification` → `badges[]` (earned vs locked) |
| Enable team leaderboard toggle | onChange → PUT | `PUT /api/gamification/team` → `enabled` |
| Team token input (32 chars) | onChange → PUT | `PUT /api/gamification/team` → `token` |
| "Generate new token" button | onClick → POST | `POST /api/gamification/team/token` |
| Leaderboard table | Display only | `GET /api/gamification/leaderboard` |

**Body Score Formula:**
```
body_score = sum over all 6 muscle_groups of:
    (exercises_done_this_week[group] / target_per_week[group]) * weight[group]
    capped at 1.0 per group
* 100

weights = { back: 0.25, neck: 0.20, wrists: 0.15, eyes: 0.15, legs: 0.15, fullbody: 0.10 }
target_per_week = { back: 7, neck: 10, wrists: 14, eyes: 14, legs: 5, fullbody: 3 }
```

**API endpoints:**
- `GET /api/gamification`
- `PUT /api/gamification/team`
- `POST /api/gamification/team/token`
- `GET /api/gamification/leaderboard`

---

## Page 7: Analytics & Reports

**Route:** `#analytics`

**Interactive Elements:**

| Element | Action | Data |
|---------|--------|------|
| Date range picker (last 7d / 30d / custom) | onChange → refetch | Query params on all analytics GETs |
| Exercises per day bar chart | Display only | `GET /api/analytics/daily` → Chart.js |
| Muscle group coverage heatmap | Display only | `GET /api/analytics/muscle_coverage` → Chart.js radar |
| Posture score trend line chart | Display only | `GET /api/analytics/body_score_trend` |
| Streak calendar (GitHub-style heatmap) | Display only | `GET /api/analytics/streak_calendar` |
| "Download CSV" button | onClick → download | `GET /api/analytics/export?format=csv` |
| "Generate weekly report" button | onClick → open | `GET /api/analytics/weekly_report` (HTML in new tab) |
| Compliance rate display (% of scheduled exercises done) | Display only | `GET /api/analytics/compliance` |

**API endpoints:**
- `GET /api/analytics/daily`
- `GET /api/analytics/muscle_coverage`
- `GET /api/analytics/body_score_trend`
- `GET /api/analytics/streak_calendar`
- `GET /api/analytics/compliance`
- `GET /api/analytics/export`
- `GET /api/analytics/weekly_report`

---

## Page 8: Plugin / Pack Manager

**Route:** `#plugins`

**Interactive Elements:**

| Element | Action | Data |
|---------|--------|------|
| Installed packs list | Display only | `GET /api/plugins` |
| Enable/disable toggle per pack | onChange → PUT | `PUT /api/plugins/{pack_id}` → `enabled` |
| Install from file (file picker .tar.gz) | onChange → POST multipart | `POST /api/plugins/install` |
| Install from URL input + button | onClick → POST | `POST /api/plugins/install` body: `{"url": "..."}` |
| Uninstall button per pack | onClick → DELETE | `DELETE /api/plugins/{pack_id}` |
| Validation status badge per pack | Display only | From `GET /api/plugins` → `valid`, `error` fields |
| Pack detail expand (shows exercises count, author, version) | onClick | Client-side expand |

**Security note displayed in UI:** "Exercise packs are pure data — no code is ever executed. Packs are validated against the exercise schema before installation."

**API endpoints:**
- `GET /api/plugins`
- `POST /api/plugins/install`
- `PUT /api/plugins/{pack_id}`
- `DELETE /api/plugins/{pack_id}`

---

## Page 9: Accessibility Settings

**Route:** `#accessibility`

**Interactive Elements:**

| Element | Action | Data |
|---------|--------|------|
| Reduced motion toggle | onChange → PUT | `PUT /api/accessibility` → `reduced_motion` |
| Audio cues toggle | onChange → PUT | `PUT /api/accessibility` → `audio_cues` |
| Audio cue volume slider (0–100) | onChange → PUT | `PUT /api/accessibility` → `audio_volume` |
| Screen reader mode toggle (verbose AT cues) | onChange → PUT | `PUT /api/accessibility` → `screen_reader_mode` |
| Font size adjustment (small/medium/large) | onChange → PUT | `PUT /api/accessibility` → `font_size` |
| High contrast mode toggle | onChange → PUT | `PUT /api/accessibility` → `high_contrast` |
| "Test audio cue" button | onClick → POST | `POST /api/accessibility/test_audio` |

**API endpoints:**
- `GET /api/accessibility`
- `PUT /api/accessibility`
- `POST /api/accessibility/test_audio`

---

## Page 10: Calendar Integration

**Route:** `#calendar`

**Interactive Elements:**

| Element | Action | Data |
|---------|--------|------|
| Google Calendar connect button | onClick → OAuth2 PKCE flow | `GET /api/calendar/auth/google` (redirects to Google) |
| Nextcloud CalDAV URL input | onChange | `PUT /api/calendar/caldav` |
| CalDAV username + password (stored in keyring) | onChange → PUT | `PUT /api/calendar/caldav` |
| Connected calendars list | Display only | `GET /api/calendar/accounts` |
| "Suppress during events" toggle per calendar | onChange → PUT | `PUT /api/calendar/accounts/{id}` |
| Disconnect calendar button | onClick → DELETE | `DELETE /api/calendar/accounts/{id}` |
| Sync status indicator (last synced) | Display only | `GET /api/calendar/status` |
| "Sync now" button | onClick → POST | `POST /api/calendar/sync` |

**API endpoints:**
- `GET /api/calendar/accounts`
- `GET /api/calendar/auth/google`
- `GET /api/calendar/auth/google/callback`
- `PUT /api/calendar/caldav`
- `PUT /api/calendar/accounts/{id}`
- `DELETE /api/calendar/accounts/{id}`
- `GET /api/calendar/status`
- `POST /api/calendar/sync`
- `GET /api/calendar/today`

---

# SECTION 9: API SPECIFICATION

Base URL: `http://127.0.0.1:7331/api`  
Authentication: Single-use session token in cookie `ap_session` (see security model Section 11)  
Content-Type: `application/json` for all POST/PUT, unless noted

---

### Daemon Control

**`GET /api/daemon/status`**  
Returns daemon state.  
Response: `{"running": true, "paused": false, "uptime_seconds": 3600, "version": "1.0.0"}`

**`POST /api/daemon/pause`**  
Pauses all timers indefinitely.  
Body: `{}`  
Response: `{"ok": true}`

**`POST /api/daemon/resume`**  
Resumes all timers.  
Body: `{}`  
Response: `{"ok": true}`

---

### Dashboard

**`GET /api/dashboard`**  
Returns today's summary.  
Response:
```json
{
  "completed_today": 5,
  "goal_today": 8,
  "next_pauses": [
    {"muscle_group": "back", "in_seconds": 1200, "exercise_name": "Cat-Cow Stretch"},
    {"muscle_group": "eyes", "in_seconds": 300, "exercise_name": "20-20-20 Eye Break"}
  ],
  "standing_state": "sitting",
  "standing_minutes_today": 45,
  "daemon_paused": false
}
```

---

### Timers

**`GET /api/timers`**  
Returns all timer configs.  
Response:
```json
{
  "timers": {
    "back": {"interval_minutes": 45, "duration_seconds": 60, "enabled": true},
    "neck": {"interval_minutes": 30, "duration_seconds": 45, "enabled": true},
    "wrists": {"interval_minutes": 20, "duration_seconds": 30, "enabled": true},
    "eyes": {"interval_minutes": 20, "duration_seconds": 25, "enabled": true},
    "legs": {"interval_minutes": 60, "duration_seconds": 45, "enabled": true},
    "fullbody": {"interval_minutes": 90, "duration_seconds": 50, "enabled": true}
  },
  "active_hours": {"start": 9, "end": 18},
  "active_weekdays": [0,1,2,3,4],
  "pause_on_fullscreen": true,
  "pomodoro_mode": false
}
```

**`PUT /api/timers`**  
Updates timer config. Partial updates accepted (only changed fields needed).  
Body: subset of the GET response structure  
Response: `{"ok": true, "config_reloaded": true}`

**`POST /api/timers/snooze`**  
Snoozes all timers.  
Body: `{"minutes": 15}`  
Response: `{"ok": true, "snoozed_until": "2026-04-02T15:30:00"}`

**`POST /api/timers/reset`**  
Resets all timers to defaults.  
Body: `{}`  
Response: `{"ok": true}`

---

### Profile

**`GET /api/profile`**  
Returns current user profile.  
Response:
```json
{
  "profile_type": "programmer",
  "intensity_cap": 2,
  "contraindications": ["carpal_tunnel_mild"],
  "gender_expr": "masc",
  "skin_tone": "s3",
  "face_variant": "a",
  "clothing_style": "casual_default",
  "reduced_motion": false,
  "audio_cues": true,
  "onboarding_complete": true
}
```

**`PUT /api/profile`**  
Updates profile fields. Partial updates accepted.  
Body: subset of profile fields  
Response: `{"ok": true}`

**`POST /api/profile/onboarding`**  
Submits onboarding questionnaire answers.  
Body:
```json
{
  "activity_type": "typing_heavy",
  "conditions": ["wrist_pain"],
  "fitness_level": "gentle",
  "standing_desk": false,
  "gender_expr": "femm",
  "skin_tone": "s2"
}
```
Response: `{"ok": true, "profile": {...full profile...}}`

---

### Exercises

**`GET /api/exercises`**  
Returns filtered exercise list.  
Query params: `muscle_group`, `intensity` (comma-sep), `q` (search), `exclude_contraindications` (bool), `pack_id`  
Response:
```json
{
  "exercises": [
    {
      "id": "back_cat_cow",
      "name": "Cat-Cow Stretch",
      "muscle_groups": ["back", "neck"],
      "intensity": 1,
      "duration_seconds": 60,
      "pack_id": "builtin",
      "contraindications": ["spinal_surgery", "herniated_disc_acute"]
    }
  ],
  "total": 1
}
```

**`GET /api/exercises/{exercise_id}`**  
Returns full exercise detail.  
Response: full `Exercise` model as JSON including `phases[]`, `research_source`, `verbal_cue`, `animation_ref`

**`POST /api/exercises/trigger`**  
Immediately triggers exercise window for given exercise.  
Body: `{"exercise_id": "back_cat_cow"}`  
Response: `{"ok": true}`

---

### Standing Desk

**`GET /api/standing`**  
Returns standing desk config.  
Response: `{"enabled": true, "ratio": "1:1", "max_standing_minutes": 45}`

**`PUT /api/standing`**  
Updates standing desk config.  
Body: subset of config fields  
Response: `{"ok": true}`

**`GET /api/standing/current`**  
Returns current posture state.  
Response: `{"state": "sitting", "duration_minutes": 23, "standing_minutes_today": 45}`

**`GET /api/standing/today`**  
Returns today's sit/stand timeline for Chart.js.  
Response: `{"timeline": [{"hour": 9, "minutes_standing": 25, "minutes_sitting": 35}, ...]}`

---

### Gamification

**`GET /api/gamification`**  
Returns gamification state.  
Response:
```json
{
  "streak_days": 7,
  "body_score": 72,
  "muscle_coverage": {"back": 0.8, "neck": 1.0, "wrists": 0.6, "eyes": 0.9, "legs": 0.5, "fullbody": 0.3},
  "badges": [
    {"id": "first_week", "name": "First Week", "earned": true, "earned_date": "2026-03-26"},
    {"id": "back_master", "name": "Back Master", "earned": false, "earned_date": null}
  ],
  "team_enabled": false
}
```

**`PUT /api/gamification/team`**  
Configures team leaderboard.  
Body: `{"enabled": true, "token": "abc123...32chars"}`  
Response: `{"ok": true}`

**`POST /api/gamification/team/token`**  
Generates a new random team token.  
Body: `{}`  
Response: `{"token": "newtoken...32chars"}`

**`GET /api/gamification/leaderboard`**  
Returns team leaderboard (local aggregation of shared-token peers).  
Response: `{"members": [{"name": "Juan", "streak": 7, "body_score": 72, "rank": 1}]}`

---

### Analytics

**`GET /api/analytics/daily`**  
Query: `?days=7` (default 7, max 365)  
Response: `{"labels": ["Mon","Tue",...], "datasets": [{"label": "Exercises", "data": [3,5,...]}]}`

**`GET /api/analytics/muscle_coverage`**  
Query: `?days=30`  
Response: `{"labels": ["Back","Neck",...], "data": [0.8, 1.0, 0.6, 0.9, 0.5, 0.3]}`

**`GET /api/analytics/body_score_trend`**  
Query: `?days=30`  
Response: `{"labels": ["2026-03-03",...], "data": [60, 65, 70, 72,...]}`

**`GET /api/analytics/streak_calendar`**  
Query: `?year=2026`  
Response: `{"weeks": [[{"date": "2026-01-01", "count": 3}, ...], ...]}`

**`GET /api/analytics/compliance`**  
Query: `?days=7`  
Response: `{"scheduled": 56, "completed": 42, "rate": 0.75}`

**`GET /api/analytics/export`**  
Query: `?format=csv&start=2026-01-01&end=2026-04-02`  
Response: `text/csv` file download  
Filename header: `Content-Disposition: attachment; filename="active-pauses-export-2026-04-02.csv"`

**`GET /api/analytics/weekly_report`**  
Response: `text/html` — full weekly report page

---

### Plugins

**`GET /api/plugins`**  
Response:
```json
{
  "packs": [
    {
      "id": "builtin",
      "name": "Built-in Exercises",
      "version": "1.0.0",
      "author": "active-pauses team",
      "exercise_count": 20,
      "enabled": true,
      "valid": true,
      "builtin": true
    }
  ]
}
```

**`POST /api/plugins/install`**  
Body: either `{"url": "https://..."}` or multipart form with `file` field (.tar.gz)  
Response: `{"ok": true, "pack_id": "yoga_breaks", "exercise_count": 8}` or `{"ok": false, "error": "Validation failed: ..."}`

**`PUT /api/plugins/{pack_id}`**  
Body: `{"enabled": true}`  
Response: `{"ok": true}`

**`DELETE /api/plugins/{pack_id}`**  
Response: `{"ok": true}` or 400 if pack is builtin

---

### Accessibility

**`GET /api/accessibility`**  
Response: `{"reduced_motion": false, "audio_cues": true, "audio_volume": 80, "screen_reader_mode": false, "font_size": "medium", "high_contrast": false}`

**`PUT /api/accessibility`**  
Body: subset of fields  
Response: `{"ok": true}`

**`POST /api/accessibility/test_audio`**  
Body: `{}`  
Plays `bell_start.ogg` once.  
Response: `{"ok": true}`

---

### Calendar

**`GET /api/calendar/accounts`**  
Response: `{"accounts": [{"id": "google_1", "type": "google", "email": "user@gmail.com", "suppress_during_events": true, "last_synced": "2026-04-02T10:00:00"}]}`

**`GET /api/calendar/auth/google`**  
Initiates OAuth2 PKCE flow. Returns 302 redirect to Google authorization URL.

**`GET /api/calendar/auth/google/callback`**  
OAuth2 callback. Exchanges code for token, stores in libsecret, redirects to `/#calendar`.

**`PUT /api/calendar/caldav`**  
Body: `{"url": "https://nextcloud.example.com/remote.php/dav", "username": "alice", "password": "secret"}`  
Password stored in libsecret, not in config.toml.  
Response: `{"ok": true, "account_id": "caldav_1"}`

**`PUT /api/calendar/accounts/{account_id}`**  
Body: `{"suppress_during_events": false}`  
Response: `{"ok": true}`

**`DELETE /api/calendar/accounts/{account_id}`**  
Removes account + revokes/deletes stored token.  
Response: `{"ok": true}`

**`GET /api/calendar/status`**  
Response: `{"last_synced": "2026-04-02T10:00:00", "next_sync": "2026-04-02T10:30:00", "event_count_today": 3}`

**`POST /api/calendar/sync`**  
Triggers immediate calendar sync.  
Response: `{"ok": true, "synced_accounts": 1, "events_fetched": 3}`

**`GET /api/calendar/today`**  
Response: `{"events": [{"title": "Team standup", "start": "2026-04-02T10:00:00", "end": "2026-04-02T10:15:00", "blocking": true}]}`

---

# SECTION 10: DATABASE SCHEMA

All models live in `src/active_pauses/db/models.py`.

```python
# src/active_pauses/db/models.py

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Date, Enum, Float, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all active-pauses models."""


class MuscleGroupEnum(str, enum.Enum):
    BACK = "back"
    NECK = "neck"
    WRISTS = "wrists"
    EYES = "eyes"
    LEGS = "legs"
    FULLBODY = "fullbody"
    SHOULDERS = "shoulders"
    HIPS = "hips"


class ProfileTypeEnum(str, enum.Enum):
    DESK_WORKER = "desk_worker"
    PROGRAMMER = "programmer"
    SENIOR = "senior"
    POSTPARTUM = "postpartum"
    GAMER = "gamer"


class PostureStateEnum(str, enum.Enum):
    SITTING = "sitting"
    STANDING = "standing"


class UserProfile(Base):
    """Single-row table representing the user's health profile and preferences.
    
    Enforced as single-row via a check constraint on id = 1.
    """
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    profile_type: Mapped[ProfileTypeEnum] = mapped_column(
        Enum(ProfileTypeEnum), nullable=False, default=ProfileTypeEnum.DESK_WORKER
    )
    intensity_cap: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    # JSON-serialized list of contraindication slugs, stored as comma-separated string
    contraindications: Mapped[str] = mapped_column(Text, nullable=False, default="")
    gender_expr: Mapped[str] = mapped_column(String(10), nullable=False, default="masc")
    skin_tone: Mapped[str] = mapped_column(String(4), nullable=False, default="s1")
    face_variant: Mapped[str] = mapped_column(String(4), nullable=False, default="a")
    clothing_style: Mapped[str] = mapped_column(String(32), nullable=False, default="casual_default")
    reduced_motion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    audio_cues: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    audio_volume: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    screen_reader_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    font_size: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    high_contrast: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Enforce single-row semantics
        Index("ix_user_profile_id", "id", unique=True),
    )


class WorkSession(Base):
    """Represents one continuous working session (daemon uptime block).
    
    A new session starts when the daemon starts; it ends when the daemon stops.
    """
    __tablename__ = "work_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Daemon version at time of session start
    daemon_version: Mapped[str] = mapped_column(String(32), nullable=False)

    exercise_logs: Mapped[list[ExerciseLog]] = relationship(back_populates="session")
    posture_events: Mapped[list[PostureEvent]] = relationship(back_populates="session")

    __table_args__ = (
        Index("ix_work_sessions_started_at", "started_at"),
    )


class ExerciseLog(Base):
    """Records each time an exercise was presented and the outcome.
    
    outcome: 'completed', 'skipped', 'snoozed', 'interrupted'
    """
    __tablename__ = "exercise_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("work_sessions.id"), nullable=False)
    exercise_id: Mapped[str] = mapped_column(String(64), nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(128), nullable=False)
    muscle_group: Mapped[MuscleGroupEnum] = mapped_column(Enum(MuscleGroupEnum), nullable=False)
    pack_id: Mapped[str] = mapped_column(String(64), nullable=False, default="builtin")
    intensity: Mapped[int] = mapped_column(Integer, nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)  # completed/skipped/snoozed/interrupted
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Actual duration in seconds (may differ from scheduled if interrupted)
    actual_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    session: Mapped[WorkSession] = relationship(back_populates="exercise_logs")

    __table_args__ = (
        Index("ix_exercise_log_session_id", "session_id"),
        Index("ix_exercise_log_scheduled_at", "scheduled_at"),
        Index("ix_exercise_log_muscle_group", "muscle_group"),
        Index("ix_exercise_log_outcome", "outcome"),
    )


class PostureEvent(Base):
    """Records transitions between sitting and standing states.
    
    A new row is created each time the user toggles standing mode.
    """
    __tablename__ = "posture_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("work_sessions.id"), nullable=False)
    state: Mapped[PostureStateEnum] = mapped_column(Enum(PostureStateEnum), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # filled on end

    session: Mapped[WorkSession] = relationship(back_populates="posture_events")

    __table_args__ = (
        Index("ix_posture_events_started_at", "started_at"),
        Index("ix_posture_events_state", "state"),
    )


class DailyStats(Base):
    """Materialized daily aggregate — updated at end of day or on first access next day.
    
    Used for analytics queries to avoid scanning full exercise_log on every request.
    """
    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    exercises_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exercises_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exercises_snoozed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    body_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    standing_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sitting_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # JSON-serialized dict: {muscle_group: completed_count}
    muscle_group_counts: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    __table_args__ = (
        Index("ix_daily_stats_stat_date", "stat_date"),
    )


class Streak(Base):
    """Current and historical streak data. Single-row (id=1).
    
    streak_days: current consecutive days with ≥2 completed exercises
    longest_streak: historical maximum
    last_active_date: the last date a qualifying day was recorded
    """
    __tablename__ = "streak"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_active_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class Badge(Base):
    """Earned badges. One row per earned badge (unearned badges are defined in code, not DB)."""
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    badge_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        UniqueConstraint("badge_id", name="uq_badges_badge_id"),
    )


class CalendarAccount(Base):
    """Connected calendar account. Token stored in libsecret, keyed by secret_key."""
    __tablename__ = "calendar_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    cal_type: Mapped[str] = mapped_column(String(16), nullable=False)  # 'google' or 'caldav'
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    # For Google: email address. For CalDAV: server URL
    identifier: Mapped[str] = mapped_column(String(256), nullable=False)
    suppress_during_events: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Key used to look up token in libsecret keyring
    secret_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())


class InstalledPack(Base):
    """Tracks installed exercise packs."""
    __tablename__ = "installed_packs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pack_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    author: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    license: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    installed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    # Path to pack directory under ~/.local/share/active-pauses/exercises/
    pack_path: Mapped[str] = mapped_column(String(512), nullable=False)
    exercise_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    validation_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

### Alembic Migration Strategy

**Baseline:** `0001_initial_schema.py` creates all 9 tables from scratch.

**Migration rules:**
1. Never use `--autogenerate` blindly — always review generated migrations before committing
2. All schema changes require an Alembic migration; never alter production DB manually
3. Migrations must be reversible (implement both `upgrade()` and `downgrade()`)
4. Data migrations (backfilling columns) are separate migrations from schema migrations
5. Column renames use a two-step migration: add new column → backfill → drop old (never `ALTER COLUMN RENAME` directly, for SQLite compatibility)

**Migration naming convention:** `{4-digit-seq}_{short_description}.py` e.g. `0002_add_posture_events_index.py`

**Alembic env.py configuration:**
```python
# db/migrations/env.py
from active_pauses.db.engine import get_engine
from active_pauses.db.models import Base

target_metadata = Base.metadata

def run_migrations_online() -> None:
    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

---

# SECTION 11: SECURITY MODEL

## 11.1 Threat Model

**What we are protecting against on a single-user local app:**

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|-----------|
| Another local user accessing SQLite data | Medium (multi-user system) | High (personal health data) | File permissions: `chmod 700 ~/.local/share/active-pauses/`; SQLite file is `600` |
| Malicious exercise pack executing arbitrary code | Low–Medium (if user installs untrusted pack) | High | TOML-only format; schema validates no executable fields; no `eval`, `exec`, `import` possible in TOML |
| CSRF against localhost web UI | Low (localhost-only) | Medium (could change config) | `SameSite=Strict` cookie; `Origin` header check on all mutating requests |
| XSS in web UI | Low | Medium | Alpine.js uses `x-text` (not `innerHTML`) for all user-controlled data; FastAPI response escaping |
| OAuth2 token theft (calendar) | Low (local filesystem) | Medium | Tokens in libsecret (not config.toml or SQLite); file permissions 600 on keyring DB |
| Privilege escalation | Very Low | High | App never requests root; systemd user service (not system service); no suid binaries |
| Calendar data exfiltration | Low | Low | Calendar is read-only (never writes events); only used to suppress notifications |
| Port scanning by other processes | Low | Low | Binds to `127.0.0.1` only (not `0.0.0.0`); session token required |

**Out of scope:** network attackers (app is fully local-first, offline-capable), nation-state actors, kernel exploits.

---

## 11.2 Plugin Sandboxing

**Why TOML-only is safe:**

TOML is a pure data format. Python's `tomllib` (stdlib) parses TOML into Python dicts/lists/strings — it never evaluates arbitrary expressions. There is no mechanism in TOML for function calls, imports, or shell execution.

**Validation layer** (`plugins/validator.py`) additionally:

1. **Forbidden key check:** Recursively walks every key in the parsed TOML tree. If any key matches the blocklist `{exec, import, script, shell, command, eval, code, python, subprocess, os, sys}`, validation fails with a clear error.

2. **Schema validation:** Every `[[exercise]]` entry is passed through the `Exercise` Pydantic model. Any field not in the model schema is rejected (`model_config = ConfigDict(extra="forbid")`).

3. **String length limits:** All string fields have maxlen constraints enforced at the Pydantic level. This prevents resource exhaustion from maliciously large strings.

4. **No file paths in packs:** Pack TOML files may not contain filesystem paths outside the pack directory. The `animation_ref` field is a slug (validated: `^[a-z0-9_]+$`), not a path.

5. **No network references:** Pack TOML files may not contain URLs in any field (the `research_source` field accepts DOI strings or plain citation text; URL format is accepted but the app never fetches the URL at runtime).

**Pack installation security:**
- Packs are extracted to `~/.local/share/active-pauses/exercises/{pack_id}/`
- Extraction uses `tarfile` with path traversal protection: any archive member whose resolved path escapes the target directory raises `SecurityError` before extraction
- After extraction, every `.toml` file is validated before the pack is registered

---

## 11.3 Calendar Token Storage

**libsecret flow:**

```
User authorizes Google Calendar
        │
        ▼
OAuth2 PKCE callback receives authorization code
        │
        ▼
Exchange code for access_token + refresh_token
        │
        ▼
secretstorage.get_keyring().set_password(
    service="active-pauses",
    username=f"calendar_{account_id}",
    password=json.dumps({"access_token": ..., "refresh_token": ..., "expires_at": ...})
)
        │
        ▼
Store only account_id + secret_key in SQLite (CalendarAccount.secret_key)
Never store tokens in config.toml or SQLite
```

**Token rotation strategy:**
- Access tokens are refreshed automatically when `expires_at - now() < 5 minutes`
- Refresh uses `requests` with the stored `refresh_token`
- New tokens overwrite the libsecret entry
- On calendar account disconnect: `secretstorage.get_keyring().delete_password(service, username)` — token is deleted, not just deactivated

**CalDAV password storage:** Same libsecret pattern. The CalDAV URL and username are stored in SQLite (`CalendarAccount.identifier`); the password is stored only in libsecret.

---

## 11.4 Localhost Web UI Authentication

**Decision: Single-use session token in a cookie**

**Rationale:** The web UI binds to `127.0.0.1` only (never `0.0.0.0`), so it is not reachable from the network. However, on a multi-user Linux system, any local user can make HTTP requests to `127.0.0.1:7331`. A session token prevents this.

**Implementation:**
1. On daemon start, a 32-byte cryptographically random token is generated: `secrets.token_hex(32)`
2. The token is written to `~/.local/share/active-pauses/web_session.token` with permissions `600`
3. When `active-pauses web` is run, the CLI reads this token and opens the browser to `http://127.0.0.1:7331/auth?token=<token>`
4. FastAPI's `/auth` endpoint sets a `SameSite=Strict; HttpOnly; Path=/` cookie `ap_session=<token>`
5. All API endpoints (except `/auth` itself) check for this cookie via a FastAPI dependency: `Depends(require_session)`
6. The token file is regenerated on every daemon restart
7. Direct browser navigation to `http://127.0.0.1:7331` without a valid cookie returns a 403 with a plain-text message: `"Run 'active-pauses web' to open the configuration UI."`

**Tradeoff:** This adds friction for power users who want to open the UI manually. Documented in README: always use `active-pauses web` to launch the browser.

---

## 11.5 Data Export Privacy

- CSV exports contain only the user's own exercise history and posture events — no identifiers beyond timestamps
- The export filename does not contain username or hostname
- Export files are written to the path specified by the user (default: current directory) — never uploaded anywhere
- The weekly HTML report is a local file; it is never transmitted. If future SMTP support is added, it will be explicitly opt-in with a clear warning that the report leaves the local machine
- Team leaderboard: the shared token is user-chosen (not a UUID generated server-side); the app never transmits data to a server. Leaderboard is implemented by the user sharing the same token across machines and the app reading a locally-maintained `leaderboard.json` synced via a user-controlled mechanism (e.g., syncthing) — **no server component, ever**

---

# SECTION 12: TESTING STRATEGY

## 12.1 Coverage Targets by Module

| Module | Target | Rationale |
|--------|--------|-----------|
| `daemon/scheduler.py` | ≥95% | Core loop — every branch matters |
| `daemon/notification.py` | ≥80% | libnotify is mocked; test action dispatch |
| `exercises/selector.py` | ≥95% | Selection algorithm — contraindications/recency |
| `exercises/loader.py` | ≥95% | Schema validation — test all error paths |
| `plugins/validator.py` | ≥95% | Security-critical — test all rejection cases |
| `gamification/streak.py` | ≥95% | Date arithmetic edge cases |
| `gamification/body_score.py` | ≥95% | Formula — property-tested |
| `web/routes/*.py` | ≥85% | API correctness |
| `db/repositories/*.py` | ≥85% | SQL correctness |
| `avatars/renderer.py` | ≥80% | Snapshot tested |
| `calendar_sync/*.py` | ≥80% | Integration tested with mock server |
| `cli/main.py` | ≥75% | CLI UX paths |

---

## 12.2 Property-Based Tests (Hypothesis)

**`test_body_score.py`:**
```python
from hypothesis import given, strategies as st
from active_pauses.gamification.body_score import calculate_body_score

@given(
    back=st.integers(min_value=0, max_value=100),
    neck=st.integers(min_value=0, max_value=100),
    wrists=st.integers(min_value=0, max_value=100),
    eyes=st.integers(min_value=0, max_value=100),
    legs=st.integers(min_value=0, max_value=100),
    fullbody=st.integers(min_value=0, max_value=100),
)
def test_body_score_always_bounded(back, neck, wrists, eyes, legs, fullbody) -> None:
    score = calculate_body_score(back=back, neck=neck, wrists=wrists,
                                  eyes=eyes, legs=legs, fullbody=fullbody)
    assert 0.0 <= score <= 100.0

@given(st.integers(min_value=0, max_value=100))
def test_body_score_monotonic_per_group(count: int) -> None:
    score_low = calculate_body_score(back=count, neck=0, wrists=0, eyes=0, legs=0, fullbody=0)
    score_high = calculate_body_score(back=count+1, neck=0, wrists=0, eyes=0, legs=0, fullbody=0)
    assert score_high >= score_low
```

**`test_scheduler.py` (snooze boundary):**
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=480))
def test_snooze_always_positive_delay(snooze_minutes: int) -> None:
    scheduler = TimerScheduler(mock_aps_scheduler())
    before = {j.id: j.next_run_time for j in scheduler.get_jobs()}
    scheduler.snooze(minutes=snooze_minutes)
    for job in scheduler.get_jobs():
        delta = job.next_run_time - before[job.id]
        assert delta.total_seconds() == snooze_minutes * 60
```

**`test_exercise_selector.py` (contraindication filtering):**
```python
from hypothesis import given, strategies as st, assume

@given(
    contraindications=st.lists(
        st.sampled_from(list(CONTRAINDICATION_SLUGS)), min_size=0, max_size=5
    )
)
def test_selector_never_returns_contraindicated_exercise(
    contraindications: list[str],
    all_exercises: list[Exercise],
) -> None:
    profile = make_profile(contraindications=contraindications)
    assume(len(all_exercises) > 0)
    for _ in range(50):
        exercise = select_exercise(all_exercises, profile, history=[])
        for c in contraindications:
            assert c not in exercise.contraindications
```

---

## 12.3 Integration Test Scenarios

**`tests/integration/test_ipc.py`:**

Fixture `live_daemon` starts the daemon as a subprocess with `--config /tmp/test-config --db /tmp/test.db`, waits for DBus service registration (up to 5s), yields a `dbus.SessionBus()` proxy, then kills the daemon on teardown.

Test scenarios:
1. `test_dbus_status_returns_running()` — call `GetStatus()`, assert `running=True`
2. `test_dbus_snooze_delays_jobs()` — call `SnoozeMinutes(10)`, then `GetStatus()`, assert `next_pause_times` all shifted
3. `test_dbus_pause_resume()` — `Pause()` → assert `paused=True` → `Resume()` → assert `paused=False`
4. `test_dbus_trigger_unknown_exercise_returns_error()` — `TriggerExercise("nonexistent")` → assert DBus exception

**`tests/integration/test_web_api.py`:**

Uses `fastapi.testclient.TestClient`. Skips session cookie validation in test mode (controlled by `ACTIVE_PAUSES_TEST_MODE=1` env var).

Tests every route with:
- Happy path (valid input → expected response shape)
- Invalid input (400 response with error message)
- Missing resource (404 response)

---

## 12.4 End-to-End: Simulate 8-Hour Workday

**`tests/e2e/test_simulate_8h.py`:**

```python
import subprocess
import json
import tempfile
from pathlib import Path

def test_simulate_8h_produces_valid_event_log(tmp_path: Path) -> None:
    """8h simulation runs in <10s, produces valid events, no side effects."""
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()

    result = subprocess.run(
        [
            "active-pauses",
            "--config", str(config_dir),
            "--data-dir", str(data_dir),
            "--simulate", "8h",
            "--output-json", str(tmp_path / "events.json"),
        ],
        capture_output=True,
        text=True,
        timeout=30,  # Must complete in 30s
    )

    assert result.returncode == 0, f"Simulation failed: {result.stderr}"

    events = json.loads((tmp_path / "events.json").read_text())

    # Verify no side effects: no notifications sent to desktop
    assert not any(e["type"] == "notification_sent" for e in events), \
        "Simulation must not send real notifications"

    # Verify plausible number of exercise events
    exercise_events = [e for e in events if e["type"] == "exercise_scheduled"]
    assert 10 <= len(exercise_events) <= 60, \
        f"Expected 10–60 exercises in 8h, got {len(exercise_events)}"

    # Verify no two exercises of same muscle group within their minimum interval
    by_group: dict[str, list[float]] = {}
    for e in exercise_events:
        group = e["muscle_group"]
        t = e["simulated_time_minutes"]
        if group not in by_group:
            by_group[group] = []
        if by_group[group]:
            gap = t - by_group[group][-1]
            assert gap >= 15, f"Group {group}: gap {gap}m is below minimum 15m"
        by_group[group].append(t)

    # Verify SQLite was written in data_dir (not user's real data_dir)
    assert (data_dir / "active-pauses.db").exists()
```

---

## 12.5 Snapshot Testing for SVG Frames

**`tests/snapshots/test_avatar_renderer.py`:**

```python
import pytest
from pathlib import Path
from active_pauses.avatars.renderer import compose_avatar_html
from active_pauses.exercises.models import Exercise
from active_pauses.db.models import UserProfile

SNAPSHOT_DIR = Path(__file__).parent / "__snapshots__"

PROFILES = [
    ("masc_s1", {"gender_expr": "masc", "skin_tone": "s1", "face_variant": "a", "clothing_style": "casual_default", "reduced_motion": False}),
    ("femm_s3", {"gender_expr": "femm", "skin_tone": "s3", "face_variant": "b", "clothing_style": "office_default", "reduced_motion": False}),
    ("nbin_s5_reduced_motion", {"gender_expr": "nbin", "skin_tone": "s5", "face_variant": "c", "clothing_style": "casual_default", "reduced_motion": True}),
]

EXERCISES = ["back_cat_cow", "neck_side_tilt", "wrists_circles", "eyes_20_20_20", "legs_seated_extensions"]

@pytest.mark.parametrize("profile_name,profile_data", PROFILES)
@pytest.mark.parametrize("exercise_id", EXERCISES)
def test_avatar_html_matches_snapshot(
    profile_name: str,
    profile_data: dict,
    exercise_id: str,
    exercise_registry: dict,
    snapshot_update: bool,  # --snapshot-update flag via conftest
) -> None:
    profile = UserProfile(**profile_data)
    exercise = exercise_registry[exercise_id]
    html = compose_avatar_html(profile, exercise)

    snapshot_file = SNAPSHOT_DIR / f"{profile_name}_{exercise_id}.html"
    if snapshot_update or not snapshot_file.exists():
        snapshot_file.write_text(html)
        return

    expected = snapshot_file.read_text()
    assert html == expected, (
        f"Avatar HTML changed for {profile_name} + {exercise_id}. "
        f"Run pytest --snapshot-update to accept changes."
    )
```

---

## 12.6 Accessibility Audit

**Web UI:** Use `axe-core` via `pytest-playwright`:

```python
# tests/e2e/test_accessibility.py
from playwright.sync_api import Page

def test_dashboard_axe_zero_violations(page: Page, live_web_server: str) -> None:
    page.goto(f"{live_web_server}/#dashboard")
    violations = page.evaluate("""
        async () => {
            const axe = await import('/axe.min.js');
            const result = await axe.run();
            return result.violations;
        }
    """)
    critical = [v for v in violations if v["impact"] in ("critical", "serious")]
    assert critical == [], f"axe-core found critical violations: {critical}"
```

**GTK4 window:** Use `pyatspi` to verify accessible names are set on all widgets:

```python
# tests/e2e/test_gtk_accessibility.py
def test_exercise_window_has_accessible_name(launched_exercise_window) -> None:
    import pyatspi
    desktop = pyatspi.Registry.getDesktop(0)
    # Find our window by accessible name
    window = find_accessible(desktop, "Exercise: Cat-Cow Stretch")
    assert window is not None, "Exercise window must have accessible name"
    progress = find_child(window, pyatspi.ROLE_PROGRESS_BAR)
    assert progress.name != "", "Progress bar must have accessible name"
```

---

## 12.7 CI Pipeline Definition

### `.github/workflows/pr-checks.yml` (runs on every PR)

```yaml
name: PR Checks

on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install ruff black mypy
      - run: ruff check src/ tests/
      - run: black --check src/ tests/
      - run: mypy --strict src/

  test-unit:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: sudo apt-get install -y libdbus-1-dev libsecret-1-dev libnotify-dev libgirepository1.0-dev
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ -v --cov=src/active_pauses --cov-report=xml --cov-fail-under=80

  test-integration:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: sudo apt-get install -y libdbus-1-dev libsecret-1-dev libnotify-dev libgirepository1.0-dev dbus-x11
      - run: pip install -e ".[dev]"
      - run: |
          export DBUS_SESSION_BUS_ADDRESS=$(dbus-launch --sh-syntax | grep DBUS_SESSION_BUS_ADDRESS | cut -d= -f2-)
          pytest tests/integration/ -v
```

### `.github/workflows/merge-main.yml` (runs on merge to main)

```yaml
name: Full Test Suite

on:
  push:
    branches: [main]

jobs:
  full-test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: sudo apt-get install -y libdbus-1-dev libsecret-1-dev libnotify-dev libgirepository1.0-dev dbus-x11 xvfb
      - run: pip install -e ".[dev]"
      - run: |
          export DBUS_SESSION_BUS_ADDRESS=$(dbus-launch --sh-syntax | grep DBUS_SESSION_BUS_ADDRESS | cut -d= -f2-)
          Xvfb :99 -screen 0 1024x768x24 &
          export DISPLAY=:99
          pytest tests/ -v --cov=src/active_pauses --cov-report=xml --cov-fail-under=85
      - uses: codecov/codecov-action@v4
        with: { files: coverage.xml }
```

### `.github/workflows/release.yml` (runs on tag `v*`)

```yaml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  build-pypi:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with: { name: pypi-dist, path: dist/ }

  build-deb:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: sudo apt-get install -y dpkg-dev fakeroot
      - run: ./scripts/build_deb.sh
      - uses: actions/upload-artifact@v4
        with: { name: deb-package, path: "*.deb" }

  build-snap:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: snapcore/action-build@v1
      - uses: actions/upload-artifact@v4
        with: { name: snap-package, path: "*.snap" }

  create-release:
    needs: [build-pypi, build-deb, build-snap]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/download-artifact@v4
      - name: Extract changelog for this version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          python scripts/extract_changelog.py "$VERSION" > release_notes.md
      - uses: softprops/action-gh-release@v2
        with:
          body_path: release_notes.md
          files: |
            pypi-dist/active_pauses-*.whl
            pypi-dist/active_pauses-*.tar.gz
            deb-package/active-pauses_*.deb
            snap-package/active-pauses_*.snap
```

---

# SECTION 13: PACKAGING & DISTRIBUTION

## 13.1 `pyproject.toml` (canonical, used by pip + build)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "active-pauses"
version = "1.0.0"
description = "A Linux health companion that guides desk workers through research-backed active breaks"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.12"
authors = [{ name = "active-pauses contributors" }]
keywords = ["health", "ergonomics", "linux", "desktop", "pomodoro"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: X11 Applications :: GTK",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Topic :: Desktop Environment",
    "Topic :: Utilities",
]
dependencies = [
    "dasbus>=1.6",
    "dbus-python>=1.3",
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
    "pydantic>=2.7",
    "pydantic-settings>=2.2",
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    "apscheduler>=3.10",
    "typer>=0.12",
    "rich>=13.7",
    "tomli-w>=1.0",
    "secretstorage>=3.3",
    "requests>=2.31",
    "vobject>=0.9",         # CalDAV iCal parsing
    "PyGObject>=3.46",      # GTK4 bindings — installed via apt on Linux
]

[project.optional-dependencies]
dev = [
    "pytest>=8.1",
    "pytest-asyncio>=0.23",
    "pytest-cov>=5.0",
    "pytest-playwright>=0.4",
    "hypothesis>=6.100",
    "mypy>=1.10",
    "ruff>=0.4",
    "black>=24.4",
    "types-requests>=2.31",
]

[project.scripts]
active-pauses = "active_pauses.cli.main:app"

[project.urls]
Homepage = "https://github.com/yourusername/active-pauses"
Documentation = "https://active-pauses.readthedocs.io"
Repository = "https://github.com/yourusername/active-pauses"
"Bug Tracker" = "https://github.com/yourusername/active-pauses/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/active_pauses"]

[tool.ruff]
src = ["src"]
line-length = 100
target-version = "py312"
select = ["E", "W", "F", "I", "B", "C4", "UP", "N", "ANN", "S", "T20"]
ignore = ["ANN101", "ANN102"]

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.mypy]
strict = true
python_version = "3.12"
mypy_path = "src"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--tb=short"

[tool.coverage.run]
source = ["src/active_pauses"]
branch = true
```

---

## 13.2 Debian Package

### `packaging/deb/control`

```
Package: active-pauses
Version: 1.0.0
Architecture: amd64
Maintainer: active-pauses contributors <hello@active-pauses.dev>
Depends: python3 (>= 3.12), python3-gi, python3-gi-cairo, gir1.2-gtk-4.0, gir1.2-notify-0.7, libsecret-1-0, python3-dbus, libnotify-bin
Recommends: libsecret-tools
Description: Linux health companion for active breaks
 active-pauses runs as a systemd user service and reminds desk workers
 to take research-backed active breaks guided by animated avatars.
 All data stays local. No root required.
Homepage: https://github.com/yourusername/active-pauses
```

### `packaging/deb/active-pauses.service` (systemd user unit)

```ini
[Unit]
Description=active-pauses health break daemon
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/active-pauses start --foreground
Restart=on-failure
RestartSec=10
# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
PrivateTmp=true
# User data directories are accessible
ReadWritePaths=%h/.local/share/active-pauses %h/.config/active-pauses

[Install]
WantedBy=graphical-session.target
```

### `packaging/deb/postinst`

```bash
#!/bin/bash
set -e

# Enable and start the systemd user service for the installing user
# $SUDO_USER is the user who ran sudo; fallback to reading from loginctl
INSTALL_USER="${SUDO_USER:-$(loginctl list-users --no-legend | awk '{print $2}' | head -1)}"

if [ -n "$INSTALL_USER" ]; then
    su -l "$INSTALL_USER" -c "systemctl --user enable active-pauses.service" || true
    su -l "$INSTALL_USER" -c "systemctl --user start active-pauses.service" || true
    echo "active-pauses: systemd user service enabled for $INSTALL_USER"
    echo "active-pauses: Open http://127.0.0.1:7331 or run 'active-pauses web' to configure"
fi
```

### `packaging/deb/prerm`

```bash
#!/bin/bash
set -e

INSTALL_USER="${SUDO_USER:-$(loginctl list-users --no-legend | awk '{print $2}' | head -1)}"

if [ -n "$INSTALL_USER" ]; then
    su -l "$INSTALL_USER" -c "systemctl --user stop active-pauses.service" || true
    su -l "$INSTALL_USER" -c "systemctl --user disable active-pauses.service" || true
fi
```

### Build script: `scripts/build_deb.sh`

```bash
#!/bin/bash
set -euo pipefail

VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
BUILD_DIR="$(mktemp -d)/active-pauses_${VERSION}_amd64"

mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/lib/systemd/user"
mkdir -p "$BUILD_DIR/usr/share/active-pauses"

# Copy packaging metadata
cp packaging/deb/control "$BUILD_DIR/DEBIAN/"
cp packaging/deb/postinst "$BUILD_DIR/DEBIAN/"
cp packaging/deb/prerm "$BUILD_DIR/DEBIAN/"
chmod 755 "$BUILD_DIR/DEBIAN/postinst" "$BUILD_DIR/DEBIAN/prerm"

# Install Python package to build dir
pip install --target "$BUILD_DIR/usr/share/active-pauses/lib" .

# Create the launcher script
cat > "$BUILD_DIR/usr/bin/active-pauses" <<'EOF'
#!/bin/bash
export PYTHONPATH="/usr/share/active-pauses/lib:$PYTHONPATH"
exec python3 -m active_pauses "$@"
EOF
chmod 755 "$BUILD_DIR/usr/bin/active-pauses"

# Copy systemd unit
cp packaging/deb/active-pauses.service "$BUILD_DIR/usr/lib/systemd/user/"

# Copy assets
cp -r assets "$BUILD_DIR/usr/share/active-pauses/"
cp -r exercise_packs "$BUILD_DIR/usr/share/active-pauses/"

# Build the .deb
dpkg-deb --build "$BUILD_DIR" "active-pauses_${VERSION}_amd64.deb"
echo "Built: active-pauses_${VERSION}_amd64.deb"
```

---

## 13.3 Snap Package

### `packaging/snap/snapcraft.yaml`

```yaml
name: active-pauses
version: "1.0.0"
summary: Linux health companion for active breaks
description: |
  active-pauses runs as a background service and reminds desk workers to take
  research-backed active breaks guided by animated avatars. Configured via
  a localhost browser UI. All data stays local. No root required.

base: core24
confinement: strict
grade: stable

apps:
  active-pauses:
    command: bin/active-pauses
    plugs:
      - desktop
      - desktop-legacy
      - wayland
      - x11
      - home
      - network-bind       # localhost:7331 web UI
      - network            # calendar OAuth2 (opt-in)
      - audio-playback     # audio cues
      - dbus               # org.activepause.Daemon
      - gsettings          # read reduced-motion system setting
      - secrets-service    # libsecret token storage

  daemon:
    command: bin/active-pauses start --foreground
    daemon: simple
    restart-condition: on-failure
    restart-delay: 10s
    stop-command: bin/active-pauses stop
    plugs:
      - desktop
      - desktop-legacy
      - wayland
      - x11
      - home
      - network-bind
      - network
      - audio-playback
      - dbus
      - gsettings
      - secrets-service

parts:
  active-pauses:
    plugin: python
    source: .
    python-packages:
      - .
    build-packages:
      - python3-dev
      - libdbus-1-dev
      - libsecret-1-dev
      - libgirepository1.0-dev
      - libcairo2-dev
      - pkg-config
    stage-packages:
      - python3-gi
      - python3-gi-cairo
      - gir1.2-gtk-4.0
      - gir1.2-notify-0.7
      - gir1.2-webkit2-4.1
      - libsecret-1-0
      - python3-dbus
      - libnotify4

slots:
  dbus-active-pauses:
    interface: dbus
    bus: session
    name: org.activepause.Daemon
```

---

# SECTION 14: FIRST SPRINT BACKLOG (Phase 1 Issues)

Sprint 1 goal: working daemon that fires notifications on schedule, logs to SQLite, and is controllable via CLI.

---

### Issue 1
**Title:** `[INFRA] Repository scaffolding: pyproject.toml, directory structure, CI skeleton`  
**Labels:** `infra`, `good first issue`, `sprint-1`  
**Story:** As a developer, I want a working repository with correct Python packaging, linting, and a passing CI pipeline so that the team can start building features immediately.  
**Acceptance Criteria:**
- `pyproject.toml` installs cleanly with `pip install -e ".[dev]"` on Ubuntu 24.04
- `ruff check src/ tests/` exits 0 on empty src/
- `mypy --strict src/` exits 0 on empty src/
- `pytest tests/` exits 0 with 0 tests collected (empty test suite passes)
- `.github/workflows/pr-checks.yml` runs lint + test jobs on push
- All directories from Section 2 created with `.gitkeep` files  
**Points:** 2

---

### Issue 2
**Title:** `[DB] SQLAlchemy models and Alembic baseline migration`  
**Labels:** `database`, `sprint-1`  
**Story:** As a developer, I want the complete database schema created and versioned with Alembic so that all other components can store data from day one.  
**Acceptance Criteria:**
- All 9 models from Section 10 defined in `src/active_pauses/db/models.py` with full type annotations
- `alembic upgrade head` on a fresh SQLite file creates all tables with correct columns and indexes
- `alembic downgrade base` cleanly drops all tables
- `mypy --strict` passes on `db/models.py` and `db/engine.py`
- `pytest tests/integration/test_db_migrations.py` passes  
**Points:** 3

---

### Issue 3
**Title:** `[EXERCISES] Pydantic exercise models and TOML schema validator`  
**Labels:** `exercises`, `sprint-1`  
**Story:** As a daemon developer, I want to load and validate exercise packs from TOML files so that exercise data is always correct before being used.  
**Acceptance Criteria:**
- `Exercise`, `ExercisePhase`, `MuscleGroup` models in `src/active_pauses/exercises/models.py` match Section 6.1 spec
- `loader.py` loads a valid TOML file and returns `list[Exercise]`
- `loader.py` raises `ExerciseLoadError` with the field name and value on schema violation
- `loader.py` rejects TOML with forbidden keys (`exec`, `import`, `script`, `shell`, `eval`)
- `pytest tests/unit/test_exercise_loader.py` passes with 100% coverage of `loader.py`  
**Points:** 3

---

### Issue 4
**Title:** `[EXERCISES] Seed exercise data: 20 exercises in builtin pack`  
**Labels:** `exercises`, `content`, `sprint-1`  
**Story:** As a user, I want 20 built-in exercises across all muscle groups so that the app is useful immediately after installation.  
**Acceptance Criteria:**
- All 20 exercises from Section 6.3 written in `exercise_packs/builtin/exercises/` TOML files
- Each exercise has all required fields including `research_source`, `verbal_cue`, and `phases`
- `active-pauses validate-pack exercise_packs/builtin/` exits 0
- `active-pauses list-exercises` shows all 20 exercises
- All 20 exercises load without error in `pytest tests/unit/test_exercise_loader.py`  
**Points:** 3

---

### Issue 5
**Title:** `[CONFIG] TOML config loader with inotify watch and defaults`  
**Labels:** `config`, `sprint-1`  
**Story:** As a daemon, I want to read `~/.config/active-pauses/config.toml` on startup and reload it within 5 seconds of any change so that users can adjust settings without restarting the daemon.  
**Acceptance Criteria:**
- `config/schema.py` Pydantic models cover all fields from the config.toml example in README
- `config/loader.py` creates `config.toml` with defaults if it doesn't exist
- `config_watcher.py` uses `inotify_simple` (or `watchdog`) to detect file changes
- Config reload is tested: write a change to a temp file, assert the daemon re-reads within 5s
- `mypy --strict` passes on all config modules  
**Points:** 2

---

### Issue 6
**Title:** `[DAEMON] asyncio daemon entry point and systemd user service unit`  
**Labels:** `daemon`, `sprint-1`  
**Story:** As a user, I want `systemctl --user start active-pauses` to start the daemon automatically on login and keep it running so that I never have to think about starting it.  
**Acceptance Criteria:**
- `daemon/main.py` starts an asyncio event loop, loads config, initializes scheduler, starts config watcher, and runs until SIGTERM
- `systemctl --user start active-pauses` starts the daemon without root on Ubuntu 24.04
- `systemctl --user status active-pauses` shows `active (running)`
- SIGTERM causes clean shutdown (all jobs cancelled, DB session closed)
- Log output goes to journald (accessible via `journalctl --user -u active-pauses`)  
**Points:** 3

---

### Issue 7
**Title:** `[DAEMON] Per-muscle-group APScheduler timer with snooze and skip`  
**Labels:** `daemon`, `scheduler`, `sprint-1`  
**Story:** As a user, I want the daemon to fire a scheduled callback for each muscle group at the configured interval so that I'm reminded to exercise the right muscles at the right time.  
**Acceptance Criteria:**
- `daemon/scheduler.py` creates one APScheduler `IntervalTrigger` job per enabled muscle group
- `scheduler.snooze(minutes=N)` shifts `next_run_time` for all jobs by N minutes
- `scheduler.skip_current()` marks the current pending exercise as skipped and resets the timer
- `scheduler.pause()` / `scheduler.resume()` pause/resume all jobs
- Active hours are respected: jobs do not fire outside `active_hours.start`–`active_hours.end`
- `pytest tests/unit/test_scheduler.py` passes including hypothesis property tests for snooze  
**Points:** 5

---

### Issue 8
**Title:** `[DAEMON] Exercise selector respecting profile contraindications and recency`  
**Labels:** `daemon`, `exercises`, `sprint-1`  
**Story:** As a user, I want the daemon to pick exercises that are safe for my health profile and that don't repeat the same exercise twice in a row so that breaks feel varied and appropriate.  
**Acceptance Criteria:**
- `exercises/selector.py` filters out exercises whose `contraindications` overlap with `profile.contraindications`
- `exercises/selector.py` filters out exercises with `intensity > profile.intensity_cap`
- Selection avoids the last 3 exercises played for each muscle group (weighted random)
- If all exercises are filtered out for a group, logs a warning and skips the break
- `pytest tests/unit/test_exercise_selector.py` passes including hypothesis property tests  
**Points:** 3

---

### Issue 9
**Title:** `[DAEMON] libnotify notification with action buttons (Do it now / Snooze / Skip)`  
**Labels:** `daemon`, `notifications`, `sprint-1`  
**Story:** As a user, I want to see a desktop notification with actionable buttons when it's time for a break so that I can choose what to do without opening a terminal.  
**Acceptance Criteria:**
- `daemon/notification.py` sends a libnotify notification with: title, body (exercise name + duration), and 3 action buttons: "Do it now", "Snooze 5m", "Skip"
- "Do it now" → DBus call triggers exercise window (stub: just logs to journald in Phase 1)
- "Snooze 5m" → calls `scheduler.snooze(minutes=5)` and sends a confirmation notification
- "Skip" → calls `scheduler.skip_current()`
- Notification sends correctly on Ubuntu 24.04 GNOME with `notify-send` test command
- `pytest tests/unit/test_notification.py` passes with mocked libnotify  
**Points:** 3

---

### Issue 10
**Title:** `[DAEMON] DBus service org.activepause.Daemon with 6 methods`  
**Labels:** `daemon`, `ipc`, `sprint-1`  
**Story:** As a CLI client, I want to communicate with the running daemon via DBus so that I can control it without shell signals or pidfiles.  
**Acceptance Criteria:**
- `daemon/ipc.py` registers `org.activepause.Daemon` on the session bus using dasbus
- Implements: `Pause()`, `Resume()`, `SnoozeMinutes(n: int)`, `GetStatus() → str`, `TriggerExercise(exercise_id: str)`, `Quit()`
- `GetStatus()` returns a JSON string with: `running`, `paused`, `next_pause_times{group: iso8601}`, `completed_today`
- DBus introspection works: `gdbus introspect --session --dest org.activepause.Daemon --object-path /org/activepause/Daemon`
- `pytest tests/integration/test_ipc.py` passes against a subprocess-launched daemon  
**Points:** 5

---

### Issue 11
**Title:** `[CLI] Typer CLI: start, stop, status, snooze, skip, pause, resume, list-exercises, trigger`  
**Labels:** `cli`, `sprint-1`  
**Story:** As a user, I want to control active-pauses from the terminal with memorable commands so that I can integrate it into my workflow without opening a browser.  
**Acceptance Criteria:**
- `active-pauses start` starts the daemon (or prints "already running")
- `active-pauses stop` sends `Quit()` via DBus
- `active-pauses status` prints a `rich` table: daemon state, next pause times per group, today's completions
- `active-pauses snooze [minutes]` (default: 15) calls `SnoozeMinutes`
- `active-pauses skip` calls `TriggerSkip` (marks current pending as skipped)
- `active-pauses pause` / `resume` call `Pause()` / `Resume()`
- `active-pauses list-exercises [--muscle-group back]` prints a rich table of loaded exercises
- `active-pauses trigger <exercise_id>` calls `TriggerExercise`
- `active-pauses --version` prints the version
- All commands have `--help` output
- `pytest tests/unit/test_cli.py` passes with mocked DBus  
**Points:** 3

---

### Issue 12
**Title:** `[DAEMON] Exercise log repository: write outcomes to SQLite`  
**Labels:** `daemon`, `database`, `sprint-1`  
**Story:** As a user, I want every exercise event (scheduled, completed, skipped, snoozed) recorded in SQLite so that analytics and streaks can be computed later.  
**Acceptance Criteria:**
- `db/repositories/exercise_log_repo.py` has: `log_scheduled()`, `log_completed()`, `log_skipped()`, `log_snoozed()`
- Daemon calls the appropriate method at each state transition
- `ExerciseLog` rows have correct `session_id` (created at daemon start)
- `pytest tests/unit/test_exercise_log_repo.py` passes with in-memory SQLite
- After a real `--simulate 2h` run, the DB contains the expected number of rows  
**Points:** 3

---

### Issue 13
**Title:** `[DAEMON] --simulate Nh dry-run mode`  
**Labels:** `daemon`, `testing`, `sprint-1`  
**Story:** As a developer, I want to simulate a full workday in seconds with `--simulate 8h` so that I can verify scheduling behavior in tests without waiting real time.  
**Acceptance Criteria:**
- `daemon/simulate.py` accelerates time: 1 real second = configurable simulated minutes
- All scheduler callbacks fire at the correct simulated times
- No libnotify notifications are sent
- No GTK windows are opened
- All events are logged to SQLite in the specified `--data-dir`
- Optionally writes a JSON event log to `--output-json`
- `active-pauses --simulate 8h` completes in < 10 seconds
- `pytest tests/e2e/test_simulate_8h.py` passes  
**Points:** 5

---

### Issue 14
**Title:** `[INFRA] GitHub PR templates and issue templates`  
**Labels:** `infra`, `docs`, `good first issue`, `sprint-1`  
**Story:** As a maintainer, I want standardized PR and issue templates so that contributions are consistent and reviewable.  
**Acceptance Criteria:**
- All 5 PR templates from Section 3 committed to `.github/PULL_REQUEST_TEMPLATE/`
- GitHub issue templates for bug report, feature request, and exercise pack submission in `.github/ISSUE_TEMPLATE/`
- `README.md` updated with the full content from Section 4  
**Points:** 1

---

## Sprint 1 Summary

| Issue | Title | Points |
|-------|-------|--------|
| 1 | Repository scaffolding | 2 |
| 2 | DB models + Alembic migration | 3 |
| 3 | Exercise Pydantic models + validator | 3 |
| 4 | 20 seed exercises | 3 |
| 5 | Config loader + inotify watch | 2 |
| 6 | Daemon entry point + systemd unit | 3 |
| 7 | APScheduler per-group timers | 5 |
| 8 | Exercise selector | 3 |
| 9 | libnotify notification + actions | 3 |
| 10 | DBus service (6 methods) | 5 |
| 11 | Typer CLI (9 commands) | 3 |
| 12 | Exercise log repository | 3 |
| 13 | --simulate Nh dry-run | 5 |
| 14 | GitHub templates | 1 |
| **Total** | | **44 points** |

*Recommended velocity for 1 senior + 1 mid developer: 40–50 points/sprint (5 weeks). This sprint is achievable within Phase 1's 5-week budget.*

---

## Self-Review: Spec Coverage Check

| Spec Section | Covered by Plan? |
|---|---|
| Phased roadmap (4+ phases) | ✅ Section 1 — 4 phases with full AC |
| Full repository structure | ✅ Section 2 — every file described |
| PR templates (5 types) | ✅ Section 3 — complete templates |
| README at v1.0 | ✅ Section 4 — full draft |
| CONTRIBUTING.md | ✅ Section 5 — full draft |
| Exercise library: 20 seed exercises | ✅ Section 6.3 — all 20 with TOML |
| Avatar SVG layer system | ✅ Section 7 — all 4 layers + naming |
| Web UI: 10 pages | ✅ Section 8 — all pages with elements + endpoints |
| API specification (all endpoints) | ✅ Section 9 — ~45 endpoints with schemas |
| Database schema (SQLAlchemy) | ✅ Section 10 — all 9 models with constraints |
| Security model | ✅ Section 11 — threat model + token storage |
| Testing strategy | ✅ Section 12 — coverage targets, hypothesis, e2e, CI |
| Packaging (.deb, snap, PyPI) | ✅ Section 13 — scripts + configs |
| Sprint 1 backlog (14 issues) | ✅ Section 14 — user stories + AC + points |
| Gamification (streaks, body score, badges) | ✅ Covered in Sections 1, 8, 10 |
| Plugin/exercise pack system | ✅ Sections 8, 9, 11 |
| Pomodoro + fullscreen detection | ✅ Section 1 Phase 3 + daemon/ structure |
| Calendar integration (Google + CalDAV) | ✅ Sections 8, 9, 10, 11 |
| Accessibility (reduced-motion, AT-SPI, ARIA) | ✅ Sections 7.4, 8, 12.6 |
| Type annotations (mypy strict) | ✅ Enforced in all CI checks |
| No root required | ✅ systemd user service; packaging postinst |
| Offline-first | ✅ All vendored JS; calendar sync opt-in only |
