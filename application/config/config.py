"""config.py"""
import os
from pathlib import Path
from threading import Lock
from typing import Any

import yaml


PANEL_CACHE_PATH = 'PANEL_CACHE_PATH'
PANEL_CONFIG_PATH = 'PANEL_CONFIG_PATH'
PANEL_NOTEBOOKS_DIR = 'PANEL_NOTEBOOKS_DIR'
_path: Path | None = None
_lock = Lock()


def set_path(path: str | Path) -> None:
    global _path
    with _lock:
        _path = path if isinstance(path, Path) else Path(path)


def get_path() -> Path:
    global _path
    with _lock:
        if _path is None:
            _path = Path(os.getenv(PANEL_CONFIG_PATH, 'config.yaml'))
        return _path


class Config:
    """Config"""
    def __init__(self):
        self.path: Path = get_path()
        self._lock = Lock()
        #self._data: dict[str, Any] = {}
        #self.load()

    @property
    def _data(self) -> dict[str, Any]:
        with self._lock:
            if self.path.exists():
                with open(self.path, 'r') as f:
                    return yaml.safe_load(f) or {}
            else:
                return {}
        
    # def load(self) -> None:
    #     with self._lock:
    #         if self.path.exists():
    #             with open(self.path, 'r') as f:
    #                 self._data = yaml.safe_load(f) or {}
    #         else:
    #             self._data = {}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __getattr__(self, key: str) -> Any:
        return self._data.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
