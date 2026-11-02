"""Semantic version parsing and comparison (SemVer 2.0.0).

Pure standard library. A version looks like ``MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]``.
Pre-release and build metadata are optional. Pre-release ordering follows the spec:
a version with a pre-release has *lower* precedence than the same version without one,
and identifiers are compared numerically when they are all digits, otherwise
lexically (case-insensitive ASCII).

Examples
--------
>>> parse("1.2.3").bump_minor()
Version(major=1, minor=3, patch=0, prerelease=(), build=())
>>> parse("1.0.0-alpha") < parse("1.0.0")
True
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import List, Tuple

_VERSION_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

_PRERELEASE_ID_RE = re.compile(r"^(?P<num>0|[1-9]\d*)$")


class VersionError(ValueError):
    """Raised when a version string does not follow SemVer."""


@dataclass(frozen=True)
class Version:
    # `slots=True` requires Python 3.10+, so it is omitted to keep 3.9 support.
    major: int
    minor: int
    patch: int
    prerelease: Tuple[str, ...] = field(default_factory=tuple)
    build: Tuple[str, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        out = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            out += "-" + ".".join(self.prerelease)
        if self.build:
            out += "+" + ".".join(self.build)
        return out

    def __repr__(self) -> str:
        return (
            f"Version(major={self.major}, minor={self.minor}, patch={self.patch}, "
            f"prerelease={self.prerelease!r}, build={self.build!r})"
        )

    def bump_major(self) -> "Version":
        return replace(self, major=self.major + 1, minor=0, patch=0, prerelease=(), build=())

    def bump_minor(self) -> "Version":
        return replace(self, minor=self.minor + 1, patch=0, prerelease=(), build=())

    def bump_patch(self) -> "Version":
        return replace(self, patch=self.patch + 1, prerelease=(), build=())

    def bump_prerelease(self, label: str = "alpha") -> "Version":
        if self.prerelease and self.prerelease[0] == label:
            last = self.prerelease[-1]
            if _PRERELEASE_ID_RE.match(last):
                head = self.prerelease[:-1] + (str(int(last) + 1),)
                return replace(self, prerelease=head)
            return replace(self, prerelease=(label, "1"))
        return replace(self, prerelease=(label, "1"))

    def is_prerelease(self) -> bool:
        return bool(self.prerelease)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return compare(self, other) == 0

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return compare(self, other) < 0

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return compare(self, other) <= 0

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return compare(self, other) > 0

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return compare(self, other) >= 0

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch, self.prerelease, self.build))


def parse(text: str) -> Version:
    """Parse a SemVer string into a :class:`Version`."""
    if not isinstance(text, str):
        raise VersionError(f"expected str, got {type(text).__name__}")
    text = text.strip()
    match = _VERSION_RE.match(text)
    if not match:
        raise VersionError(f"not a valid semantic version: {text!r}")

    return Version(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        prerelease=tuple(match.group("prerelease").split(".")) if match.group("prerelease") else (),
        build=tuple(match.group("build").split(".")) if match.group("build") else (),
    )


def _prerelease_key(pre: Tuple[str, ...]) -> Tuple[int, Tuple]:
    """Return a sort key for a prerelease tuple.

    A missing prerelease sorts *after* any present prerelease, so this is
    only used to compare two versions that both have a prerelease.
    """
    key: List[Tuple[int, str]] = []
    for ident in pre:
        num = _PRERELEASE_ID_RE.match(ident)
        if num:
            # numeric identifiers have LOWER precedence than alphanumeric ones
            # (marker 0 < 1); the zfill keeps numeric order correct within that band
            key.append((0, ident.zfill(10)))
        else:
            key.append((1, ident.lower()))
    # a tuple of (marker, value) compares element by element; a shorter tuple
    # that is a prefix sorts first, which matches the spec ("fewer identifiers
    # has lower precedence").
    return tuple(key)


def compare(a: Version, b: Version) -> int:
    """Return -1, 0 or 1 depending on whether ``a < b``, ``a == b`` or ``a > b``."""
    if a.major != b.major:
        return -1 if a.major < b.major else 1
    if a.minor != b.minor:
        return -1 if a.minor < b.minor else 1
    if a.patch != b.patch:
        return -1 if a.patch < b.patch else 1

    # prerelease precedence
    if not a.prerelease and not b.prerelease:
        return 0
    if not a.prerelease:
        return 1
    if not b.prerelease:
        return -1
    ka = _prerelease_key(a.prerelease)
    kb = _prerelease_key(b.prerelease)
    if ka == kb:
        return 0
    return -1 if ka < kb else 1


def __getattr__(name: str):  # pragma: no cover - convenience operator
    raise AttributeError(name)
