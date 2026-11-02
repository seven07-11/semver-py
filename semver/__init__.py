"""Parse, compare and increment semantic version numbers (SemVer 2.0.0)."""

__version__ = "0.1.0"

from .core import Version, parse, compare, VersionError

__all__ = ["Version", "parse", "compare", "VersionError"]
