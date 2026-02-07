"""Framework exceptions and exit-code mapping for cli-root-yo."""

from __future__ import annotations


class CliRootYoError(Exception):
    """Base exception for all cli-root-yo framework errors."""

    exit_code: int = 1


class ContextNotInitializedError(CliRootYoError):
    """Raised when get_context() is called before runtime initialization."""

    exit_code: int = 1

    def __init__(self) -> None:
        super().__init__("RuntimeContext has not been initialized.")


class RegistryFrozenError(CliRootYoError):
    """Raised when a registration is attempted after the registry is frozen."""

    exit_code: int = 1

    def __init__(self, action: str = "register") -> None:
        super().__init__(f"Cannot {action}: command registry is frozen.")


class RegistryConflictError(CliRootYoError):
    """Raised when a command name collision is detected."""

    exit_code: int = 1

    def __init__(self, path: str, detail: str = "") -> None:
        msg = f"Registration conflict at '{path}'"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class PluginLoadError(CliRootYoError):
    """Raised when a plugin fails to import or raises during registration."""

    exit_code: int = 1

    def __init__(self, plugin_name: str, reason: str = "") -> None:
        msg = f"Failed to load plugin '{plugin_name}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.plugin_name = plugin_name


class SpecValidationError(CliRootYoError):
    """Raised when CliSpec validation fails."""

    exit_code: int = 1

    def __init__(self, detail: str) -> None:
        super().__init__(f"Invalid CliSpec: {detail}")

