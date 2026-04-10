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
