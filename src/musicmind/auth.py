"""Apple Music API authentication.

Handles ES256 JWT developer token generation and Music User Token management.
"""

from __future__ import annotations

import time

import jwt

from musicmind.config import MusicMindConfig

# Developer tokens are valid for up to 6 months (Apple's max)
TOKEN_EXPIRY_SECONDS = 15_777_000  # ~6 months


class AuthManager:
    """Manages Apple Music API authentication tokens."""

    def __init__(self, config: MusicMindConfig) -> None:
        self._config = config
        self._developer_token: str | None = None
        self._developer_token_expiry: float = 0.0

    @property
    def developer_token(self) -> str:
        """Get a valid developer token, generating a new one if expired."""
        now = time.time()
        if self._developer_token and now < self._developer_token_expiry:
            return self._developer_token

        self._developer_token = self._generate_developer_token()
        self._developer_token_expiry = now + TOKEN_EXPIRY_SECONDS - 60  # 1min buffer
        return self._developer_token

    @property
    def music_user_token(self) -> str:
        """Get the Music User Token from config."""
        if not self._config.has_user_token:
            raise ValueError(
                "Music User Token not configured. "
                "Run `uv run python -m musicmind.setup` to authorize."
            )
        return self._config.music_user_token

    def auth_headers(self) -> dict[str, str]:
        """Return headers dict with both auth tokens for Apple Music API requests."""
        headers = {"Authorization": f"Bearer {self.developer_token}"}
        if self._config.has_user_token:
            headers["Music-User-Token"] = self.music_user_token
        return headers

    def _generate_developer_token(self) -> str:
        """Generate an ES256-signed JWT developer token."""
        now = int(time.time())
        payload = {
            "iss": self._config.team_id,
            "iat": now,
            "exp": now + TOKEN_EXPIRY_SECONDS,
        }
        headers = {
            "alg": "ES256",
            "kid": self._config.key_id,
        }
        return jwt.encode(
            payload,
            self._config.private_key,
            algorithm="ES256",
            headers=headers,
        )
