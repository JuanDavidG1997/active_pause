"""TOML schema validation: forbidden key detection."""
from __future__ import annotations

FORBIDDEN_KEYS = frozenset({"exec", "import", "script", "shell", "eval"})


def check_forbidden_keys(data: object, path: str = "") -> None:
    """Recursively check for forbidden keys in parsed TOML data."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key in FORBIDDEN_KEYS:
                raise ForbiddenKeyError(key, path)
            check_forbidden_keys(value, f"{path}.{key}" if path else key)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            check_forbidden_keys(item, f"{path}[{i}]")


class ForbiddenKeyError(ValueError):
    def __init__(self, key: str, path: str) -> None:
        self.key = key
        self.path = path
        super().__init__(f"Forbidden key '{key}' found at path '{path}'")
