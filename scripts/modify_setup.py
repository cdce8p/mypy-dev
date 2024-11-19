from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path
import re
import subprocess
import sys

from packaging.version import InvalidVersion, Version, parse

setup_py_file = Path(__file__).parents[1] / "mypy/setup.py"
pyproject_file = Path(__file__).parents[1] / "mypy/pyproject.toml"

readme_pat = re.compile(
    r"(readme\s*=\s*\{\s*text\s*=\s*\"\"\")"
    r"(?:.|\n)*"
    r"(\"\"\",\s*content-type\s*=\s*\"text\/x-rst\"\})"
)
readme_replace = r"\g<1>\nDevelopment releases for mypy.\n\nUse at your own risk!\n\g<2>"
name_pat = re.compile(r"(name\s*=\s*\")[\w-]+(\")")
name_replace = r"\g<1>mypy-dev\g<2>"
version_pat = re.compile(r"(version=)[^,]+(,)")
homepage_pat = re.compile(r"Homepage\s+=\s+\".+\"\n")
project_url_repo_pat = re.compile(r"(Repository\s+=\s+\")[\w:\/\.]+(\")")
project_url_repo_replace = r"\g<1>https://github.com/cdce8p/mypy-dev\g<2>"
project_url_changelog_pat = re.compile(r"Changelog\s+=\s+\"[\w:\/\.]+\"\n")


def modify_setup_py(version: Version) -> tuple[str, int]:
    orig_data = data = setup_py_file.read_text()
    res = 0
    # version
    orig_data = data
    data = version_pat.sub(rf'\g<1>"{version}"\g<2>', data ,1)
    if orig_data == data:
        print("ERROR: Could not replace 'version'")
        res = 1
    return data, res


def modify_pyproject() -> tuple[str, int]:
    orig_data = data = pyproject_file.read_text()
    res = 0
    # pyproject.name
    orig_data = data
    data = name_pat.sub(name_replace, data, 1)
    if orig_data == data:
        print("ERROR: Could not replace 'project.name'")
        res = 1
    orig_data = data
    data = readme_pat.sub(readme_replace, data, 1)
    if orig_data == data:
        print("ERROR: Could not replace 'project.readme.text'")
    # project.urls.Repository
    orig_data = data
    data = project_url_repo_pat.sub(project_url_repo_replace, data, 1)
    if orig_data == data:
        print("ERROR: Could not replace 'project.urls.Repository'")
        res = 1
    # project.urls.Homepage
    orig_data = data
    data = homepage_pat.sub("", data, 1)
    if orig_data == data:
        print("ERROR: Could not remove 'project.urls.Homepage'")
        res = 1
    # project.urls.Changelog
    orig_data = data
    data = project_url_changelog_pat.sub("", data, 1)
    if orig_data == data:
        print("ERROR: Could not remove 'project.urls.Changelog'")
        res = 1
    return data, res


def git_set_assume_unchanged() -> None:
    subprocess.check_output([
        "git", "-C", "mypy", "update-index", "--assume-unchanged", "setup.py", "pyproject.toml"
    ])


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = ArgumentParser()
    parser.add_argument("version", metavar="VERSION")
    args = parser.parse_args()
    try:
        version = parse(args.version)
    except InvalidVersion as ex:
        print(f"ERROR: {ex}")
        return 1
    print(f"Version: {version}")

    if not setup_py_file.is_file() or not pyproject_file.is_file():
        print("ERROR: Submodule not initialized")
        return 1

    setup_py_data, res = modify_setup_py(version)
    if res == 1:
        return 1

    print("Write updated setup.py")
    setup_py_file.write_text(setup_py_data)

    pyproject_data, res = modify_pyproject()
    if res == 1:
        return 1

    print("Write updated pyproject.toml")
    pyproject_file.write_text(pyproject_data)

    print("Update index - assume-unchanged")
    git_set_assume_unchanged()

    return 0


if __name__ == "__main__":
    sys.exit(main())
