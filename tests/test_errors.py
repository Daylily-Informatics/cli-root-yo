"""Tests for cli_root_yo.errors."""

from __future__ import annotations

import pytest

from cli_root_yo.errors import (
    CliRootYoError,
    ContextNotInitializedError,
    PluginLoadError,
    RegistryConflictError,
    RegistryFrozenError,
    SpecValidationError,
)


class TestCliRootYoError:
    def test_base_exception(self):
        err = CliRootYoError("boom")
        assert str(err) == "boom"
        assert err.exit_code == 1
        assert isinstance(err, Exception)

    def test_all_subclasses_inherit_base(self):
        for cls in [
            ContextNotInitializedError,
            RegistryFrozenError,
            RegistryConflictError,
            PluginLoadError,
            SpecValidationError,
        ]:
            assert issubclass(cls, CliRootYoError)


class TestContextNotInitializedError:
    def test_message(self):
        err = ContextNotInitializedError()
        assert "not been initialized" in str(err)
        assert err.exit_code == 1


class TestRegistryFrozenError:
    def test_default_message(self):
        err = RegistryFrozenError()
        assert "frozen" in str(err)

    def test_custom_action(self):
        err = RegistryFrozenError("add_group")
        assert "add_group" in str(err)


class TestRegistryConflictError:
    def test_path_only(self):
        err = RegistryConflictError("config")
        assert "config" in str(err)

    def test_path_with_detail(self):
        err = RegistryConflictError("config", "already exists as a command")
        assert "config" in str(err)
        assert "already exists as a command" in str(err)


class TestPluginLoadError:
    def test_name_only(self):
        err = PluginLoadError("my_plugin")
        assert "my_plugin" in str(err)
        assert err.plugin_name == "my_plugin"

    def test_name_with_reason(self):
        err = PluginLoadError("my_plugin", "ModuleNotFoundError")
        assert "my_plugin" in str(err)
        assert "ModuleNotFoundError" in str(err)


class TestSpecValidationError:
    def test_message(self):
        err = SpecValidationError("prog_name is empty")
        assert "prog_name is empty" in str(err)
        assert "Invalid CliSpec" in str(err)

