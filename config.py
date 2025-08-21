from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_database_path() -> Path:
    return get_base_dir() / "student_mgmt.db"


def get_settings_path() -> Path:
    return get_base_dir() / "settings.json"


def _default_settings() -> Dict[str, Any]:
    return {
        "theme": "flatly",
        "geometry": "1024x640",
        "zoomed": False,
    }


def load_settings() -> Dict[str, Any]:
    path = get_settings_path()
    if not path.exists():
        return _default_settings()
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return _default_settings()
            return {**_default_settings(), **data}
    except Exception:
        return _default_settings()


def save_settings(settings: Dict[str, Any]) -> None:
    path = get_settings_path()
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        # If saving settings fails, silently ignore to avoid crashing the app
        pass


