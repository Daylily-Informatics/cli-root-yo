"""cli-core-yo: Reusable CLI kernel for unified command-line interfaces."""

try:
    from cli_core_yo._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
