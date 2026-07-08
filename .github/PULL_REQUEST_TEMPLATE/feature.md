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
- [ ] All new public functions have docstrings
- [ ] All new functions are type-annotated
- [ ] CHANGELOG.md updated under `[Unreleased]` section
- [ ] `prefers-reduced-motion` respected (if animation changes)
- [ ] No new root-required operations introduced
- [ ] No new network calls outside of explicitly opt-in features (calendar sync)
- [ ] Plugin sandbox: no arbitrary code execution paths added

### Related issues / PRs

<!-- List any related issues or PRs. Use "Closes #N" to auto-close. -->
