"""Tests for cli_core_yo.xdg."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from cli_core_yo.spec import XdgSpec
from cli_core_yo.xdg import resolve_paths


@pytest.fixture()
def xdg_spec():
    return XdgSpec(app_dir_name="testapp")


class TestResolvePaths:
    def test_env_var_overrides(self, tmp_path: Path, xdg_spec: XdgSpec):
        env = {
            "XDG_CONFIG_HOME": str(tmp_path / "cfg"),
            "XDG_DATA_HOME": str(tmp_path / "data"),
            "XDG_STATE_HOME": str(tmp_path / "state"),
            "XDG_CACHE_HOME": str(tmp_path / "cache"),
        }
        with patch.dict(os.environ, env, clear=False):
            paths = resolve_paths(xdg_spec)
        assert paths.config == tmp_path / "cfg" / "testapp"
        assert paths.data == tmp_path / "data" / "testapp"
        assert paths.state == tmp_path / "state" / "testapp"
        assert paths.cache == tmp_path / "cache" / "testapp"
        # Directories must be created
        assert paths.config.is_dir()
        assert paths.data.is_dir()

    def test_linux_defaults(self, tmp_path: Path, xdg_spec: XdgSpec):
        remove_keys = ["XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"]
        cleaned = {k: v for k, v in os.environ.items() if k not in remove_keys}
        with (
            patch.dict(os.environ, cleaned, clear=True),
            patch("cli_core_yo.xdg._is_macos", return_value=False),
            patch("cli_core_yo.xdg.Path.home", return_value=tmp_path),
        ):
            paths = resolve_paths(xdg_spec)
        assert paths.config == tmp_path / ".config" / "testapp"
        assert paths.data == tmp_path / ".local" / "share" / "testapp"
        assert paths.state == tmp_path / ".local" / "state" / "testapp"
        assert paths.cache == tmp_path / ".cache" / "testapp"

    def test_macos_defaults(self, tmp_path: Path, xdg_spec: XdgSpec):
        remove_keys = ["XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"]
        cleaned = {k: v for k, v in os.environ.items() if k not in remove_keys}
        with (
            patch.dict(os.environ, cleaned, clear=True),
            patch("cli_core_yo.xdg._is_macos", return_value=True),
            patch("cli_core_yo.xdg.Path.home", return_value=tmp_path),
        ):
            paths = resolve_paths(xdg_spec)
        assert paths.config == tmp_path / ".config" / "testapp"
        assert paths.data == tmp_path / "Library" / "Application Support" / "testapp"
        assert paths.state == tmp_path / "Library" / "Logs" / "testapp"
        assert paths.cache == tmp_path / "Library" / "Caches" / "testapp"


class TestLegacyMigration:
    def test_copies_legacy_file(self, tmp_path: Path):
        legacy_dir = tmp_path / "legacy"
        legacy_dir.mkdir()
        (legacy_dir / "old.json").write_text('{"key": "val"}')

        spec = XdgSpec(
            app_dir_name="testapp",
            legacy_macos_config_dir=str(legacy_dir),
            legacy_copy_files=["old.json"],
        )
        env = {"XDG_CONFIG_HOME": str(tmp_path / "cfg")}
        with (
            patch.dict(os.environ, env, clear=False),
            patch("cli_core_yo.xdg._is_macos", return_value=True),
        ):
            paths = resolve_paths(spec)
        target = paths.config / "old.json"
        assert target.exists()
        assert target.read_text() == '{"key": "val"}'

    def test_does_not_overwrite_existing(self, tmp_path: Path):
        legacy_dir = tmp_path / "legacy"
        legacy_dir.mkdir()
        (legacy_dir / "old.json").write_text("legacy")

        cfg_dir = tmp_path / "cfg" / "testapp"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "old.json").write_text("existing")

        spec = XdgSpec(
            app_dir_name="testapp",
            legacy_macos_config_dir=str(legacy_dir),
            legacy_copy_files=["old.json"],
        )
        env = {"XDG_CONFIG_HOME": str(tmp_path / "cfg")}
        with (
            patch.dict(os.environ, env, clear=False),
            patch("cli_core_yo.xdg._is_macos", return_value=True),
        ):
            paths = resolve_paths(spec)
        assert (paths.config / "old.json").read_text() == "existing"

    def test_skips_on_linux(self, tmp_path: Path):
        legacy_dir = tmp_path / "legacy"
        legacy_dir.mkdir()
        (legacy_dir / "old.json").write_text("legacy")

        spec = XdgSpec(
            app_dir_name="testapp",
            legacy_macos_config_dir=str(legacy_dir),
            legacy_copy_files=["old.json"],
        )
        env = {"XDG_CONFIG_HOME": str(tmp_path / "cfg")}
        with (
            patch.dict(os.environ, env, clear=False),
            patch("cli_core_yo.xdg._is_macos", return_value=False),
        ):
            paths = resolve_paths(spec)
        assert not (paths.config / "old.json").exists()

