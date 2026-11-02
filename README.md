# semver-py

[![CI](https://github.com/seven07-11/semver-py/actions/workflows/ci.yml/badge.svg)](https://github.com/seven07-11/semver-py/actions/workflows/ci.yml)

Parse, compare and increment [Semantic Versioning](https://semver.org) strings
(`MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`) using only the Python standard library —
no dependencies, works on Python 3.9+.

## Install

```bash
pip install .
```

Or run it straight from the source tree:

```bash
python -m semver 1.2.3
```

## Library usage

```python
from semver import parse, Version

v = parse("1.2.3")
print(v.bump_minor())           # 1.3.0
print(v.bump_prerelease("rc"))  # 1.2.3-rc.1

parse("1.0.0-alpha") < parse("1.0.0")   # True
parse("1.0.0-alpha.1") < parse("1.0.0-alpha.2")  # True
parse("1.0.0-rc.1") < parse("1.0.0")    # True
```

Precedence follows the SemVer 2.0.0 spec exactly:

- A pre-release version has *lower* precedence than the same version without a pre-release.
- Pre-release identifiers are compared numerically when all-numeric, otherwise case-insensitively.
- Build metadata never affects precedence.

## Command line

```text
# validate / normalise
python -m semver 1.2.3
1.2.3

# compare two versions -> -1 / 0 / 1
python -m semver 1.0.0 2.0.0 --compare
-1

# bump
python -m semver 1.2.3 --bump minor
1.3.0

# sort
python -m semver 1.0.0 1.0.0-rc.1 1.2.0 --sort
1.0.0-rc.1
1.0.0
1.2.0
```

## Development

Tests use the standard library:

```bash
python -m unittest discover -s tests -v
```

## License

MIT
