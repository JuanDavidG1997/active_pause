"""inotify watch on config.toml; triggers reload callback on change."""
from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    """Watchdog event handler that calls reload_callback when config file changes."""

    def __init__(self, config_path: Path, reload_callback: Callable[[], None]) -> None:
        super().__init__()
        self._config_path = config_path.resolve()
        self._reload_callback = reload_callback

    def on_modified(self, event: FileSystemEvent) -> None:
        if isinstance(event, FileModifiedEvent):
            if Path(str(event.src_path)).resolve() == self._config_path:
                logger.info("Config file changed, reloading...")
                try:
                    self._reload_callback()
                except Exception as e:
                    logger.error("Config reload failed: %s", e)


class ConfigWatcher:
    """Watches config.toml for changes and triggers reload."""

    def __init__(self, config_path: Path, reload_callback: Callable[[], None]) -> None:
        self._config_path = config_path
        self._reload_callback = reload_callback
        self._observer: Any = None

    def start(self) -> None:
        """Start watching the config file directory."""
        handler = ConfigFileHandler(self._config_path, self._reload_callback)
        self._observer = Observer()
        self._observer.schedule(handler, str(self._config_path.parent), recursive=False)
        self._observer.start()
        logger.info("Config watcher started for %s", self._config_path)

    def stop(self) -> None:
        """Stop the file watcher."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None
