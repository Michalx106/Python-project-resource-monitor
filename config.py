"""Configuration utilities for the resource monitor application.

This module provides helper functions to persist and retrieve user settings
from a ``config.json`` file located in the repository root. The configuration
currently stores the update interval, history length and threshold values used
by the application.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

# ``config.py`` lives in the repository root, therefore ``CONFIG_FILE`` points
# directly to ``config.json`` in the same directory.
CONFIG_FILE = Path(__file__).with_name("config.json")

# Default configuration used when the file does not exist or is invalid.
DEFAULT_CONFIG: Dict[str, Any] = {
    "update_interval_ms": 1000,
    "history_length": 60,
    "cpu_threshold": 90,
    "ram_threshold": 90,
}


def load_config() -> Dict[str, Any]:
    """Load application configuration from ``config.json``.

    Returns
    -------
    Dict[str, Any]
        Configuration dictionary with default values filled in for any
        missing keys.
    """

    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
        return {**DEFAULT_CONFIG, **data}
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Persist configuration to ``config.json``.

    Parameters
    ----------
    config:
        Dictionary containing configuration values to save.
    """

    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

