"""Command-line entry point for semver-py."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .core import VersionError, parse


def _cmd_bump(text: str, which: str) -> str:
    v = parse(text)
    if which == "major":
        return str(v.bump_major())
    if which == "minor":
        return str(v.bump_minor())
    if which == "patch":
        return str(v.bump_patch())
    return str(v)  # unreachable


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="semver",
        description="Parse and compare semantic version numbers.",
    )
    parser.add_argument("versions", nargs="+", help="version strings to operate on")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="print -1/0/1 comparing the two given versions",
    )
    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="bump a version and print the result",
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help="sort the given versions ascending and print them",
    )
    args = parser.parse_args(argv)

    try:
        versions = [parse(v) for v in args.versions]
    except VersionError as error:
        print(f"semver: {error}", file=sys.stderr)
        return 2

    if args.compare:
        if len(versions) != 2:
            print("semver: --compare needs exactly two versions", file=sys.stderr)
            return 2
        from .core import compare

        print(compare(versions[0], versions[1]))
        return 0

    if args.bump:
        print(_cmd_bump(args.versions[0], args.bump))
        return 0

    if args.sort:
        for v in sorted(versions):
            print(v)
        return 0

    # default: validate and echo parsed form
    for v in versions:
        print(v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
