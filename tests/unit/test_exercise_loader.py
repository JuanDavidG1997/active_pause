"""Comprehensive tests for active_pauses.exercises.loader with 100% coverage."""
from __future__ import annotations

from pathlib import Path

import pytest

from active_pauses.exercises.loader import ExerciseLoadError, load_exercise_file, load_exercise_pack
from active_pauses.exercises.models import Exercise
from active_pauses.exercises.schema import ForbiddenKeyError

# ---------------------------------------------------------------------------
# Helper: minimal valid exercise TOML content
# ---------------------------------------------------------------------------

VALID_EXERCISE_TOML = """\
[[exercise]]
id = "neck_roll"
name = "Neck Roll"
muscle_groups = ["neck"]
intensity = 1
duration_seconds = 30
rest_seconds = 10
animation_ref = "neck_roll.gif"
research_source = "https://example.com/research"
verbal_cue = "Slowly roll your head in a circle"
bilateral = false

[[exercise.phases]]
name = "move"
duration_seconds = 5
cue = "Roll left"

[[exercise.phases]]
name = "rest"
duration_seconds = 5
cue = "Return to center"
"""


def _write_toml(tmp_path: Path, content: str, filename: str = "exercises.toml") -> Path:
    p = tmp_path / filename
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# 1. Happy path: valid TOML with one exercise
# ---------------------------------------------------------------------------


def test_load_valid_single_exercise(tmp_path: Path) -> None:
    path = _write_toml(tmp_path, VALID_EXERCISE_TOML)
    result = load_exercise_file(path)

    assert isinstance(result, list)
    assert len(result) == 1
    ex = result[0]
    assert isinstance(ex, Exercise)
    assert ex.id == "neck_roll"
    assert ex.name == "Neck Roll"
    assert ex.intensity == 1
    assert ex.duration_seconds == 30
    assert len(ex.phases) == 2


# ---------------------------------------------------------------------------
# 2. Missing required field: no `id`
# ---------------------------------------------------------------------------


def test_missing_id_raises_load_error(tmp_path: Path) -> None:
    toml = """\
[[exercise]]
name = "Neck Roll"
muscle_groups = ["neck"]
intensity = 1
duration_seconds = 30
rest_seconds = 10
animation_ref = "neck_roll.gif"
research_source = "https://example.com"
verbal_cue = "Roll slowly"

[[exercise.phases]]
name = "move"
duration_seconds = 5
cue = "Roll left"
"""
    path = _write_toml(tmp_path, toml)
    with pytest.raises(ExerciseLoadError):
        load_exercise_file(path)


# ---------------------------------------------------------------------------
# 3. Invalid intensity value
# ---------------------------------------------------------------------------


def test_invalid_intensity_raises_load_error(tmp_path: Path) -> None:
    toml = VALID_EXERCISE_TOML.replace("intensity = 1", "intensity = 5")
    path = _write_toml(tmp_path, toml)
    with pytest.raises(ExerciseLoadError, match="neck_roll"):
        load_exercise_file(path)


# ---------------------------------------------------------------------------
# 4. Invalid id format (contains spaces)
# ---------------------------------------------------------------------------


def test_invalid_id_format_raises_load_error(tmp_path: Path) -> None:
    toml = VALID_EXERCISE_TOML.replace('id = "neck_roll"', 'id = "has spaces"')
    path = _write_toml(tmp_path, toml)
    with pytest.raises(ExerciseLoadError):
        load_exercise_file(path)


# ---------------------------------------------------------------------------
# 5. Invalid duration_seconds (< 10)
# ---------------------------------------------------------------------------


def test_invalid_duration_too_short_raises_load_error(tmp_path: Path) -> None:
    toml = VALID_EXERCISE_TOML.replace("duration_seconds = 30", "duration_seconds = 5")
    path = _write_toml(tmp_path, toml)
    with pytest.raises(ExerciseLoadError):
        load_exercise_file(path)


# ---------------------------------------------------------------------------
# 6 & 7. Forbidden keys — parametrized
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "extra_line,expected_key",
    [
        ('exec = "rm -rf /"', "exec"),
        ('script = "malicious.sh"', "script"),
        ('shell = "/bin/bash"', "shell"),
        ('eval = "dangerous()"', "eval"),
        ('import = "os"', "import"),
    ],
)
def test_forbidden_key_at_top_level(
    tmp_path: Path, extra_line: str, expected_key: str
) -> None:
    toml = f"{extra_line}\n{VALID_EXERCISE_TOML}"
    path = _write_toml(tmp_path, toml)
    with pytest.raises(ForbiddenKeyError) as exc_info:
        load_exercise_file(path)
    assert exc_info.value.key == expected_key


def test_forbidden_key_nested_in_dict(tmp_path: Path) -> None:
    """Forbidden key nested inside a sub-table."""
    toml = """\
[metadata]
script = "evil.sh"

""" + VALID_EXERCISE_TOML
    path = _write_toml(tmp_path, toml)
    with pytest.raises(ForbiddenKeyError) as exc_info:
        load_exercise_file(path)
    assert exc_info.value.key == "script"
    assert "metadata" in exc_info.value.path


# ---------------------------------------------------------------------------
# 8. Empty exercise list
# ---------------------------------------------------------------------------


def test_empty_exercise_list(tmp_path: Path) -> None:
    toml = "exercise = []\n"
    path = _write_toml(tmp_path, toml)
    result = load_exercise_file(path)
    assert result == []


# ---------------------------------------------------------------------------
# 9. Multiple exercises
# ---------------------------------------------------------------------------


def test_multiple_exercises(tmp_path: Path) -> None:
    extra = """\
[[exercise]]
id = "shoulder_shrug"
name = "Shoulder Shrug"
muscle_groups = ["shoulders"]
intensity = 2
duration_seconds = 20
rest_seconds = 5
animation_ref = "shoulder_shrug.gif"
research_source = "https://example.com"
verbal_cue = "Shrug up then drop"

[[exercise.phases]]
name = "move"
duration_seconds = 3
cue = "Shrug up"

[[exercise]]
id = "eye_blink"
name = "Eye Blink"
muscle_groups = ["eyes"]
intensity = 1
duration_seconds = 15
rest_seconds = 0
animation_ref = "eye_blink.gif"
research_source = "https://example.com"
verbal_cue = "Blink rapidly"

[[exercise.phases]]
name = "move"
duration_seconds = 2
cue = "Blink"
"""
    toml = VALID_EXERCISE_TOML + extra
    path = _write_toml(tmp_path, toml)
    result = load_exercise_file(path)
    assert len(result) == 3
    ids = [ex.id for ex in result]
    assert "neck_roll" in ids
    assert "shoulder_shrug" in ids
    assert "eye_blink" in ids


# ---------------------------------------------------------------------------
# 10. Non-existent file raises ExerciseLoadError
# ---------------------------------------------------------------------------


def test_nonexistent_file_raises_load_error(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.toml"
    with pytest.raises(ExerciseLoadError, match="Failed to read"):
        load_exercise_file(missing)


# ---------------------------------------------------------------------------
# Extra: exercise list is not a list (wrong type)
# ---------------------------------------------------------------------------


def test_exercise_key_not_a_list(tmp_path: Path) -> None:
    toml = 'exercise = "not a list"\n'
    path = _write_toml(tmp_path, toml)
    with pytest.raises(ExerciseLoadError, match="Expected 'exercise' to be a list"):
        load_exercise_file(path)


# ---------------------------------------------------------------------------
# Extra: load_exercise_pack loads from directory
# ---------------------------------------------------------------------------


def test_load_exercise_pack_multiple_files(tmp_path: Path) -> None:
    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    _write_toml(pack_dir, VALID_EXERCISE_TOML, "a_neck.toml")
    extra_toml = """\
[[exercise]]
id = "eye_blink"
name = "Eye Blink"
muscle_groups = ["eyes"]
intensity = 1
duration_seconds = 15
rest_seconds = 0
animation_ref = "eye_blink.gif"
research_source = "https://example.com"
verbal_cue = "Blink rapidly"

[[exercise.phases]]
name = "move"
duration_seconds = 2
cue = "Blink"
"""
    _write_toml(pack_dir, extra_toml, "b_eyes.toml")
    result = load_exercise_pack(pack_dir)
    assert len(result) == 2


def test_load_exercise_pack_empty_dir(tmp_path: Path) -> None:
    pack_dir = tmp_path / "empty_pack"
    pack_dir.mkdir()
    result = load_exercise_pack(pack_dir)
    assert result == []


# ---------------------------------------------------------------------------
# Extra: raw entry is not a dict (unusual but possible in malformed TOML)
# ---------------------------------------------------------------------------


def test_non_dict_exercise_entry_uses_index_in_error(tmp_path: Path) -> None:
    """If an exercise entry is somehow not a dict, the error uses 'index N'."""
    # We can't create this via TOML (TOML array items would always be tables here),
    # but we can test the loader with a patched data structure by writing a TOML
    # with a mixed array. TOML doesn't allow mixed arrays in inline style cleanly;
    # instead test via monkey-patching tomllib.load.
    import unittest.mock as mock

    path = tmp_path / "fake.toml"
    path.write_bytes(b"")  # empty valid TOML file

    fake_data: dict[str, object] = {"exercise": ["not_a_dict"]}
    with mock.patch("active_pauses.exercises.loader.tomllib.load", return_value=fake_data):
        with pytest.raises(ExerciseLoadError, match="index 0"):
            load_exercise_file(path)
