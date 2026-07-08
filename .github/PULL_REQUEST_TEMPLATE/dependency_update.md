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
