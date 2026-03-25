"""Tests for config module — loading and saving configuration."""

from __future__ import annotations

import json

import pytest

from musicmind.config import MusicMindConfig, load_config, save_config, CONFIG_FILE


class TestMusicMindConfig:
    def test_valid_config(self, tmp_path) -> None:
        key_file = tmp_path / "key.p8"
        key_file.write_text("-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----")
        cfg = MusicMindConfig(
            team_id="TEAM123456",
            key_id="KEY1234567",
            private_key_path=str(key_file),
            music_user_token="token123",
        )
        assert cfg.team_id == "TEAM123456"
        assert cfg.storefront == "it"  # default
        assert cfg.has_user_token is True

    def test_empty_user_token(self) -> None:
        cfg = MusicMindConfig(
            team_id="T",
            key_id="K",
            private_key_path="/tmp/fake.p8",
        )
        assert cfg.has_user_token is False

    def test_private_key_read(self, tmp_path) -> None:
        key_file = tmp_path / "key.p8"
        key_file.write_text("-----BEGIN PRIVATE KEY-----\nKEYDATA\n-----END PRIVATE KEY-----")
        cfg = MusicMindConfig(
            team_id="T",
            key_id="K",
            private_key_path=str(key_file),
        )
        assert "KEYDATA" in cfg.private_key

    def test_private_key_file_missing(self) -> None:
        cfg = MusicMindConfig(
            team_id="T",
            key_id="K",
            private_key_path="/nonexistent/key.p8",
        )
        with pytest.raises(FileNotFoundError):
            _ = cfg.private_key


class TestSaveConfig:
    def test_save_creates_file(self, tmp_path, monkeypatch) -> None:
        config_dir = tmp_path / "musicmind"
        config_file = config_dir / "config.json"
        monkeypatch.setattr("musicmind.config.CONFIG_DIR", config_dir)
        monkeypatch.setattr("musicmind.config.CONFIG_FILE", config_file)

        save_config({"team_id": "T", "key_id": "K"})

        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["team_id"] == "T"

    def test_save_sets_permissions(self, tmp_path, monkeypatch) -> None:
        config_dir = tmp_path / "musicmind"
        config_file = config_dir / "config.json"
        monkeypatch.setattr("musicmind.config.CONFIG_DIR", config_dir)
        monkeypatch.setattr("musicmind.config.CONFIG_FILE", config_file)

        save_config({"team_id": "T"})

        mode = config_file.stat().st_mode & 0o777
        assert mode == 0o600


class TestLoadConfig:
    def test_load_missing_file(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setattr("musicmind.config.CONFIG_FILE", tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config()

    def test_load_valid_config(self, tmp_path, monkeypatch) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "team_id": "TEAM123456",
            "key_id": "KEY1234567",
            "private_key_path": "/tmp/key.p8",
            "music_user_token": "tok",
            "storefront": "us",
        }))
        monkeypatch.setattr("musicmind.config.CONFIG_FILE", config_file)

        cfg = load_config()
        assert cfg.team_id == "TEAM123456"
        assert cfg.storefront == "us"
