from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Final


MYPY_VERSION_FILE: Final = "mypy/mypy/version.py"
VERSION_PATTERN = re.compile(r"(\d+)\.(\d+)\.(\d+)([ab])(\d+)")

class PreRelease(StrEnum):
    ALPHA = "a"
    BETA = "b"


@dataclass(order=True)
class VersionType:
    major: int
    minor: int
    patch: int
    pre: PreRelease
    n: int


def read_mypy_version_from_file() -> str:
    content = Path(MYPY_VERSION_FILE).read_text().splitlines()
    version_line = [line for line in content if line.startswith("__version__")][0]
    version = version_line.partition(" = ")[2].strip('"').removesuffix("+dev")
    return version


def parse_version(s: str) -> VersionType:
    major, minor, patch, pre, n = VERSION_PATTERN.match(s).groups()
    return VersionType(int(major), int(minor), int(patch), PreRelease(pre), int(n))


def read_existing_tags(prefix: str) -> list[VersionType]:
    proc = subprocess.run(shlex.split("git tag --list"), capture_output=True)
    stdout = sorted(proc.stdout.decode().splitlines(), key=lambda s: parse_version(s))
    return sorted([parse_version(item) for item in stdout if item.startswith(prefix)])


def find_next_version(version: str, tags: list[VersionType], beta: bool = False) -> str:
    match tags:
        case [*_, VersionType(pre=pre, n=n)]:
            n += 1
        case _:
            pre = PreRelease.ALPHA
            n = 1
    if beta and pre is PreRelease.ALPHA:
        pre = PreRelease.BETA
        n = 1
    return f"{version}{pre}{n}"


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--beta", action=argparse.BooleanOptionalAction)
    args = parser.parse_args(argv)

    version = read_mypy_version_from_file()
    tags = read_existing_tags(version)
    next_version = find_next_version(version, tags, args.beta)

    print(next_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
