from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scripts.next_version import find_next_version, parse_version, read_existing_tags


def test_read_existing_tags() -> None:
    mock = MagicMock()
    mock.stdout = "1.17.0a1\n1.18.0a1\n1.18.0a10\n1.18.0a2\n1.18.0a3\n1.18.0b1".encode()
    with patch("subprocess.run", return_value=mock):
        assert read_existing_tags("1.18.0") == [
            parse_version(tag) for tag in [
                "1.18.0a1",
                "1.18.0a2",
                "1.18.0a3",
                "1.18.0a10",
                "1.18.0b1",
            ]
        ]


@pytest.mark.parametrize(
    ["version", "tags", "beta", "next_version"],
    [
        pytest.param(
            "1.18.0",
            ["1.18.0a1", "1.18.0a2", "1.18.0a10"],
            False,
            "1.18.0a11",
        ),
        pytest.param(
            "1.18.0",
            ["1.18.0a1", "1.18.0a2", "1.18.0a10"],
            True,
            "1.18.0b1",
        ),
        pytest.param(
            "1.18.0",
            ["1.18.0a1", "1.18.0a2", "1.18.0b1"],
            True,
            "1.18.0b2",
        ),
    ]
)
def test_find_next_version(
    version: str, tags: list[str], beta: bool, next_version: str
) -> None:
    tags_parsed = [parse_version(tag) for tag in tags]
    with patch("scripts.next_version.read_existing_tags", return_value=tags):
        assert find_next_version(version, tags_parsed, beta) == next_version
