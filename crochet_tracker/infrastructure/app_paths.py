"""Where the user's data lives (RF-17).

`%APPDATA%\\CrochetTracker` on Windows, `~/.local/share/CrochetTracker` elsewhere,
and `CROCHET_TRACKER_DATA` as an override for tests and portable installs.
"""

import os
from pathlib import Path

DATA_ENV_VAR = "CROCHET_TRACKER_DATA"
APP_DIR_NAME = "CrochetTracker"
GUIDES_DIR_NAME = "guides"
DB_FILE_NAME = "crochet.db"
LOCK_FILE_NAME = "app.lock"
ERROR_LOG_NAME = "error.log"


def data_dir() -> Path:
    """Return the data folder, creating it if it does not exist."""
    override = os.environ.get(DATA_ENV_VAR)
    if override:
        path = Path(override)
    else:
        base = Path(os.environ.get("APPDATA") or Path.home() / ".local" / "share")
        path = base / APP_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path
