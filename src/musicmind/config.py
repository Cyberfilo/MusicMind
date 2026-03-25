"""Configuration loading for MusicMind MCP.

Loads settings from ~/.config/musicmind/config.json.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stderr))

CONFIG_DIR = Path.home() / ".config" / "musicmind"
CONFIG_FILE = CONFIG_DIR / "config.json"
DB_FILE = CONFIG_DIR / "musicmind.db"


class MusicMindConfig(BaseModel):
    """Configuration for the MusicMind MCP server."""

    team_id: str = Field(description="Apple Developer Team ID (10-char)")
    key_id: str = Field(description="Apple Music API Key ID (10-char)")
    private_key_path: str = Field(description="Path to .p8 private key file")
    music_user_token: str = Field(default="", description="Music User Token from OAuth")
    storefront: str = Field(default="it", description="Apple Music storefront country code")

    @property
    def private_key(self) -> str:
        """Read the private key from disk."""
        key_path = Path(self.private_key_path).expanduser()
        if not key_path.exists():
            raise FileNotFoundError(f"Private key not found: {key_path}")
        return key_path.read_text().strip()

    @property
    def has_user_token(self) -> bool:
        return bool(self.music_user_token)


def load_config() -> MusicMindConfig:
    """Load configuration from ~/.config/musicmind/config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_FILE}\n"
            f"Run `uv run python -m musicmind.setup` to create it."
        )

    raw = json.loads(CONFIG_FILE.read_text())
    return MusicMindConfig(**raw)


def save_config(data: dict[str, Any]) -> None:
    """Save configuration to ~/.config/musicmind/config.json with secure permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    CONFIG_FILE.chmod(0o600)
    logger.info("Config saved to %s", CONFIG_FILE)
