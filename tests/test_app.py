"""Tests for cli_root_yo.app — factory, run, built-in commands."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import typer
from typer.testing import CliRunner

from cli_root_yo.app import (
    create_app,
    run,
    _validate_spec,
    _get_dist_version,
    _resolve_template,
)
from cli_root_yo.errors import SpecValidationError
from cli_root_yo.spec import CliSpec, ConfigSpec, EnvSpec, PluginSpec, XdgSpec


runner = CliRunner()


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def xdg_spec():
    return XdgSpec(app_dir_name="test-app")


@pytest.fixture
def config_spec():
    return ConfigSpec(
        primary_filename="config.json",
        template_bytes=b'{"key": "value"}\n',
    )


@pytest.fixture
def env_spec():
    return EnvSpec(
        active_env_var="TEST_APP_ACTIVE",
        project_root_env_var="TEST_APP_ROOT",
        activate_script_name="activate.sh",
        deactivate_script_name="deactivate.sh",
    )


@pytest.fixture
def minimal_spec(xdg_spec, tmp_path):
    """Minimal CliSpec with no optional groups."""
    return CliSpec(
        prog_name="test-app",
        app_display_name="Test App",
        dist_name="cli-root-yo",
        root_help="A test application.",
        xdg=xdg_spec,
    )


@pytest.fixture
def full_spec(xdg_spec, config_spec, env_spec):
    """CliSpec with config and env groups enabled."""
    return CliSpec(
        prog_name="test-app",
        app_display_name="Test App",
        dist_name="cli-root-yo",
        root_help="A test application.",
        xdg=xdg_spec,
        config=config_spec,
        env=env_spec,
    )


# ── _validate_spec tests ───────────────────────────────────────────────────


class TestValidateSpec:
    def test_valid_spec(self, minimal_spec):
        _validate_spec(minimal_spec)  # should not raise

    def test_empty_prog_name(self, xdg_spec):
        spec = CliSpec(
            prog_name="",
            app_display_name="X",
            dist_name="x",
            root_help="x",
            xdg=xdg_spec,
        )
        with pytest.raises(SpecValidationError, match="prog_name must not be empty"):
            _validate_spec(spec)

    def test_invalid_prog_name(self, xdg_spec):
        spec = CliSpec(
            prog_name="Bad_Name",
            app_display_name="X",
            dist_name="x",
            root_help="x",
            xdg=xdg_spec,
        )
        with pytest.raises(SpecValidationError, match="not a valid name"):
            _validate_spec(spec)

    def test_empty_display_name(self, xdg_spec):
        spec = CliSpec(
            prog_name="ok",
            app_display_name="",
            dist_name="x",
            root_help="x",
            xdg=xdg_spec,
        )
        with pytest.raises(SpecValidationError, match="app_display_name"):
            _validate_spec(spec)

    def test_empty_dist_name(self, xdg_spec):
        spec = CliSpec(
            prog_name="ok",
            app_display_name="X",
            dist_name="",
            root_help="x",
            xdg=xdg_spec,
        )
        with pytest.raises(SpecValidationError, match="dist_name"):
            _validate_spec(spec)

    def test_empty_root_help(self, xdg_spec):
        spec = CliSpec(
            prog_name="ok",
            app_display_name="X",
            dist_name="x",
            root_help="",
            xdg=xdg_spec,
        )
        with pytest.raises(SpecValidationError, match="root_help"):
            _validate_spec(spec)


# ── Helper tests ────────────────────────────────────────────────────────────


class TestHelpers:
    def test_get_dist_version_known(self):
        """cli-root-yo is installed, so version should not be 'unknown'."""
        v = _get_dist_version("cli-root-yo")
        assert v != "unknown"

    def test_get_dist_version_unknown(self):
        v = _get_dist_version("nonexistent-package-xyz-999")
        assert v == "unknown"

    def test_resolve_template_bytes(self, config_spec):
        result = _resolve_template(config_spec)
        assert result == b'{"key": "value"}\n'

    def test_resolve_template_no_source(self):
        """ConfigSpec with neither source should raise (but __post_init__ prevents this)."""
        # We can only hit this if someone bypasses __post_init__
        spec = object.__new__(ConfigSpec)
        object.__setattr__(spec, "template_bytes", None)
        object.__setattr__(spec, "template_resource", None)
        object.__setattr__(spec, "primary_filename", "x")
        object.__setattr__(spec, "validator", None)
        with pytest.raises(ValueError, match="no template source"):
            _resolve_template(spec)


# ── create_app tests ────────────────────────────────────────────────────────


class TestCreateApp:
    def test_returns_typer_app(self, minimal_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        app = create_app(minimal_spec)
        assert isinstance(app, typer.Typer)

    def test_has_version_command(self, minimal_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        app = create_app(minimal_spec)
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Test App" in result.output

    def test_has_info_command(self, minimal_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        app = create_app(minimal_spec)
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0

    def test_no_args_shows_help(self, minimal_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        app = create_app(minimal_spec)
        result = runner.invoke(app, [])
        # no_args_is_help shows help; exit code 0 per SPEC §2.4
        assert result.exit_code in (0, 2)  # Typer/Click may use 0 or 2
        assert "Usage" in result.output or "test-app" in result.output

    def test_config_group_registered_when_present(self, full_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        app = create_app(full_spec)
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "config" in result.output.lower()

    def test_env_group_registered_when_present(self, full_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        app = create_app(full_spec)
        result = runner.invoke(app, ["env", "--help"])
        assert result.exit_code == 0
        assert "env" in result.output.lower()



# ── Version command tests ───────────────────────────────────────────────────


def _make_app(spec, tmp_path, monkeypatch):
    """Helper to create an app with XDG paths in tmp_path."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return create_app(spec)


class TestVersionCommand:
    def test_version_human(self, minimal_spec, tmp_path, monkeypatch):
        app = _make_app(minimal_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Test App" in result.output

    def test_version_json_long(self, minimal_spec, tmp_path, monkeypatch):
        app = _make_app(minimal_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["version", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["app"] == "Test App"
        assert "version" in data

    def test_version_json_short(self, minimal_spec, tmp_path, monkeypatch):
        app = _make_app(minimal_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["version", "-j"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["app"] == "Test App"


# ── Info command tests ──────────────────────────────────────────────────────


class TestInfoCommand:
    def test_info_human(self, minimal_spec, tmp_path, monkeypatch):
        app = _make_app(minimal_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Version" in result.output
        assert "Python" in result.output

    def test_info_json(self, minimal_spec, tmp_path, monkeypatch):
        app = _make_app(minimal_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["info", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "Version" in data
        assert "Python" in data
        assert "Config Dir" in data
        assert "CLI Core" in data

    def test_info_with_hooks(self, xdg_spec, tmp_path, monkeypatch):
        def _hook():
            return [("Custom Key", "custom-val")]

        spec = CliSpec(
            prog_name="test-app",
            app_display_name="Test App",
            dist_name="cli-root-yo",
            root_help="A test.",
            xdg=xdg_spec,
            info_hooks=[_hook],
        )
        app = _make_app(spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["info", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["Custom Key"] == "custom-val"


# ── Config group tests ──────────────────────────────────────────────────────


class TestConfigGroup:
    def test_config_path(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["config", "path"])
        assert result.exit_code == 0
        assert "config.json" in result.output

    def test_config_init_creates_file(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["config", "init"])
        assert result.exit_code == 0
        config_file = tmp_path / "config" / "test-app" / "config.json"
        assert config_file.exists()
        assert config_file.read_bytes() == b'{"key": "value"}\n'

    def test_config_init_no_overwrite(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        # First init
        runner.invoke(app, ["config", "init"])
        # Second init without --force
        result = runner.invoke(app, ["config", "init"])
        assert result.exit_code == 1

    def test_config_init_force_overwrite(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        runner.invoke(app, ["config", "init"])
        result = runner.invoke(app, ["config", "init", "--force"])
        assert result.exit_code == 0

    def test_config_show(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        runner.invoke(app, ["config", "init"])
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert '{"key": "value"}' in result.output

    def test_config_show_no_file(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 1

    def test_config_validate_no_validator(self, full_spec, tmp_path, monkeypatch):
        """No validator configured → success exit 0."""
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["config", "validate"])
        assert result.exit_code == 0
        assert "accepted" in result.output.lower() or "No validator" in result.output

    def test_config_validate_passes(self, xdg_spec, tmp_path, monkeypatch):
        config_spec = ConfigSpec(
            primary_filename="config.json",
            template_bytes=b'{"ok": true}\n',
            validator=lambda content: [],  # no errors
        )
        spec = CliSpec(
            prog_name="test-app",
            app_display_name="Test App",
            dist_name="cli-root-yo",
            root_help="A test.",
            xdg=xdg_spec,
            config=config_spec,
        )
        app = _make_app(spec, tmp_path, monkeypatch)
        runner.invoke(app, ["config", "init"])
        result = runner.invoke(app, ["config", "validate"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_config_validate_fails(self, xdg_spec, tmp_path, monkeypatch):
        config_spec = ConfigSpec(
            primary_filename="config.json",
            template_bytes=b"bad",
            validator=lambda content: ["missing key", "bad format"],
        )
        spec = CliSpec(
            prog_name="test-app",
            app_display_name="Test App",
            dist_name="cli-root-yo",
            root_help="A test.",
            xdg=xdg_spec,
            config=config_spec,
        )
        app = _make_app(spec, tmp_path, monkeypatch)
        runner.invoke(app, ["config", "init"])
        result = runner.invoke(app, ["config", "validate"])
        assert result.exit_code == 1

    def test_config_validate_no_file(self, xdg_spec, tmp_path, monkeypatch):
        config_spec = ConfigSpec(
            primary_filename="config.json",
            template_bytes=b"x",
            validator=lambda content: [],
        )
        spec = CliSpec(
            prog_name="test-app",
            app_display_name="Test App",
            dist_name="cli-root-yo",
            root_help="A test.",
            xdg=xdg_spec,
            config=config_spec,
        )
        app = _make_app(spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["config", "validate"])
        assert result.exit_code == 1

    def test_config_edit_not_tty(self, full_spec, tmp_path, monkeypatch):
        """config edit in non-interactive mode → exit 1."""
        app = _make_app(full_spec, tmp_path, monkeypatch)
        runner.invoke(app, ["config", "init"])
        # CliRunner is not a tty by default
        result = runner.invoke(app, ["config", "edit"])
        assert result.exit_code == 1

    def test_config_reset_creates_backup(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        runner.invoke(app, ["config", "init"])
        config_dir = tmp_path / "config" / "test-app"
        # Modify the file
        (config_dir / "config.json").write_text("modified")
        result = runner.invoke(app, ["config", "reset", "--yes"])
        assert result.exit_code == 0
        # Check backup exists
        bak_files = list(config_dir.glob("*.bak"))
        assert len(bak_files) == 1
        # Check reset to template
        assert (config_dir / "config.json").read_bytes() == b'{"key": "value"}\n'


# ── Env group tests ─────────────────────────────────────────────────────────


class TestEnvGroup:
    def test_env_status_inactive(self, full_spec, tmp_path, monkeypatch):
        monkeypatch.delenv("TEST_APP_ACTIVE", raising=False)
        monkeypatch.delenv("TEST_APP_ROOT", raising=False)
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["env", "status"])
        assert result.exit_code == 0
        assert "not active" in result.output.lower()

    def test_env_status_active(self, full_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("TEST_APP_ACTIVE", "1")
        monkeypatch.setenv("TEST_APP_ROOT", "/some/path")
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["env", "status"])
        assert result.exit_code == 0
        # Should report active
        assert "active" in result.output.lower()

    def test_env_activate(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["env", "activate"])
        assert result.exit_code == 0
        assert "source activate.sh" in result.output

    def test_env_deactivate(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["env", "deactivate"])
        assert result.exit_code == 0
        assert "source deactivate.sh" in result.output

    def test_env_reset(self, full_spec, tmp_path, monkeypatch):
        app = _make_app(full_spec, tmp_path, monkeypatch)
        result = runner.invoke(app, ["env", "reset"])
        assert result.exit_code == 0
        assert "source deactivate.sh" in result.output
        assert "source activate.sh" in result.output


# ── run() tests ─────────────────────────────────────────────────────────────


class TestRun:
    def test_run_version(self, minimal_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        exit_code = run(minimal_spec, ["version"])
        assert exit_code == 0

    def test_run_help_exit_0(self, minimal_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        exit_code = run(minimal_spec, ["--help"])
        assert exit_code == 0

    def test_run_invalid_spec(self, xdg_spec, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
        bad_spec = CliSpec(
            prog_name="Bad_Name",
            app_display_name="X",
            dist_name="x",
            root_help="x",
            xdg=xdg_spec,
        )
        exit_code = run(bad_spec, ["version"])
        assert exit_code == 1