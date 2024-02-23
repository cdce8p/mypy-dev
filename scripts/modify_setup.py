from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path
import re
import subprocess
import sys

from packaging.version import InvalidVersion, Version, parse

file = Path(__file__).parents[1] / "mypy/setup.py"

long_desc_pat = re.compile(r"(long_description = \"\"\")(?:.|\n)*(\"\"\"\.lstrip\(\))")
long_desc_replace = r"\g<1>\nDevelopment releases for mypy.\n\nUse at your own risk!\n\g<2>"
name_pat = re.compile(r"(    name=\")[\w-]+(\",)")
name_replace = r"\g<1>mypy-dev\g<2>"
version_pat = re.compile(r"(    version=).+(,)")
url_pat = re.compile(r"    url=\".+\",\n")
project_url_repo_pat = re.compile(r"(        \"Repository\": \")[\w:\/\.]+(\",)")
project_url_repo_replace = r"\g<1>https://github.com/cdce8p/mypy-dev\g<2>"
project_url_changelog_pat = re.compile(r"        \"Changelog\": \"[\w:\/\.]+\",\n")


def modify_setup_py(version: Version) -> tuple[str, int]:
    orig_data = data = file.read_text()
    res = 0
    # long_description
    data = long_desc_pat.sub(long_desc_replace, data, 1)
    if orig_data == data:
        print("ERROR: Could not replace 'long_description'")
        res = 1
    # name
    orig_data = data
    data = name_pat.sub(name_replace, data, 1)
    if orig_data == data:
        print("ERROR: Could not replace 'name'")
        res = 1
    # version
    orig_data = data
    data = version_pat.sub(rf'\g<1>"{version}"\g<2>', data ,1)
    if orig_data == data:
        print("ERROR: Could not replace 'version'")
        res = 1
    # url
    orig_data = data
    data = url_pat.sub("", data, 1)
    if orig_data == data:
        print("ERROR: Could not remove 'url'")
        res = 1
    # project_urls - Repository
    orig_data = data
    data = project_url_repo_pat.sub(project_url_repo_replace, data, 1)
    if orig_data == data:
        print("ERROR: Could not replace 'project_urls' - 'Repository'")
        res = 1
    # project_urls - Changelog
    orig_data = data
    data = project_url_changelog_pat.sub("", data, 1)
    if orig_data == data:
        print("ERROR: Could not remove 'project_urls' - 'Changelog'")
        res = 1
    return data, res


def git_set_assume_unchanged() -> None:
    subprocess.check_output(["git", "-C", "mypy", "update-index", "--assume-unchanged", "setup.py"])


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

    if not file.is_file():
        print("ERROR: Submodule not initialized")
        return 1

    data, res = modify_setup_py(version)
    if 0 and res == 1:
        return 1

    print("Write updated file")
    file.write_text(data)

    print("Update index - assume-unchanged")
    git_set_assume_unchanged()

    return 0


if __name__ == "__main__":
    sys.exit(main())
