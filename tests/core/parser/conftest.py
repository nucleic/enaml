# ------------------------------------------------------------------------------
# Copyright (c) 2018-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import tomllib
from typing import Any

import pytest


SOURCE_MARKER = "# --- source ---"
INVALID_ROOT = Path(__file__).resolve().parent / "invalid"
INVALID_DIR = INVALID_ROOT / "python"
PYTHON_INVALID_DIR = INVALID_ROOT / "python"
ENAML_INVALID_DIR = INVALID_ROOT / "enaml"
ROOT_KEYS = {
    "messages",
    "parser_version",
    "minimum_python",
    "maximum_python",
    "skip_reason",
    "expectations",
    "start",
    "end_line",
    "end_offset",
}
EXPECTATION_KEYS = {
    "messages",
    "parser_version",
    "runtime_minimum",
    "runtime_maximum",
    "start",
    "end_line",
    "end_offset",
}


class FixtureFormatError(ValueError):
    """Raised when an invalid-syntax fixture header is malformed."""


@dataclass(frozen=True)
class InvalidExpectation:
    messages: tuple[str, ...]
    parser_version: tuple[int, int] | None
    start: tuple[int, int] | None
    end_line: int | None
    end_offset: int | None


@dataclass(frozen=True)
class InvalidFixture:
    path: Path
    source: str
    minimum_python: tuple[int, int] | None
    maximum_python: tuple[int, int] | None
    skip_reason: str | None
    expectations: tuple[
        tuple[
            tuple[int, int] | None,
            tuple[int, int] | None,
            InvalidExpectation,
        ],
        ...,
    ]

    @property
    def fixture_id(self):
        return self.path.relative_to(INVALID_ROOT).as_posix()

    def is_supported(self, version: tuple[int, int]) -> bool:
        if self.minimum_python is not None and version < self.minimum_python:
            return False
        if self.maximum_python is not None and version > self.maximum_python:
            return False
        return True

    def select_expectation(
        self, version: tuple[int, int]
    ) -> InvalidExpectation:
        matches = [
            expectation
            for minimum, maximum, expectation in self.expectations
            if (minimum is None or version >= minimum)
            and (maximum is None or version <= maximum)
        ]
        if len(matches) != 1:
            raise FixtureFormatError(
                f"{self.path}: expected exactly one expectation for "
                f"Python {version[0]}.{version[1]}, found {len(matches)}"
            )
        return matches[0]


def _fail(path: Path, message: str) -> FixtureFormatError:
    return FixtureFormatError(f"{path}: {message}")


def _version(value: Any, path: Path, field: str) -> tuple[int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(item, int) and not isinstance(item, bool) for item in value)
    ):
        raise _fail(path, f"{field} must be a two-item integer array")
    if value[0] != 3 or value[1] < 0:
        raise _fail(path, f"{field} must identify a Python 3 version")
    return value[0], value[1]


def _optional_version(
    value: Any, path: Path, field: str
) -> tuple[int, int] | None:
    return None if value is None else _version(value, path, field)


def _messages(value: Any, path: Path, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise _fail(path, f"{field} must be an array of strings")
    return tuple(value)


def _coordinate(
    value: Any, path: Path, field: str
) -> tuple[int, int] | None:
    if value is None:
        return None
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(item, int) and item > 0 for item in value)
    ):
        raise _fail(path, f"{field} must be a two-item positive integer array")
    return value[0], value[1]


def _positive_integer(value: Any, path: Path, field: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise _fail(path, f"{field} must be a positive integer")
    return value


def _split_header(text: str, path: Path) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    marker_indexes = [
        index for index, line in enumerate(lines) if line.rstrip("\r\n") == SOURCE_MARKER
    ]
    if len(marker_indexes) != 1:
        raise _fail(path, f"expected exactly one {SOURCE_MARKER!r} marker")
    marker_index = marker_indexes[0]
    header_lines = []
    for line in lines[:marker_index]:
        line = line.rstrip("\r\n")
        if not line.startswith("#"):
            raise _fail(path, "all lines before the source marker must be comments")
        header_lines.append(line[2:] if line.startswith("# ") else line[1:])
    source = "".join(lines[marker_index + 1 :])
    return "\n".join(header_lines), source


def parse_invalid_fixture(path: Path) -> InvalidFixture:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    header, source = _split_header(text, path)
    try:
        document = tomllib.loads(header)
    except tomllib.TOMLDecodeError as exc:
        raise _fail(path, f"invalid TOML header: {exc}") from exc

    unknown = set(document) - ROOT_KEYS
    if unknown:
        raise _fail(path, f"unknown top-level fields: {sorted(unknown)}")

    root_messages = _messages(
        document.get("messages", []), path, "messages"
    )
    minimum_python = _optional_version(
        document.get("minimum_python"), path, "minimum_python"
    )
    maximum_python = _optional_version(
        document.get("maximum_python"), path, "maximum_python"
    )
    if (
        minimum_python is not None
        and maximum_python is not None
        and minimum_python > maximum_python
    ):
        raise _fail(path, "minimum_python must not exceed maximum_python")
    skip_reason = document.get("skip_reason")
    if (
        minimum_python is not None or maximum_python is not None
    ) and not isinstance(skip_reason, str):
        raise _fail(path, "skip_reason is required with Python bounds")
    if skip_reason is not None and not isinstance(skip_reason, str):
        raise _fail(path, "skip_reason must be a string")

    raw_expectations = document.get("expectations")
    if raw_expectations is None:
        raw_expectations = [{}]
    elif not isinstance(raw_expectations, list) or not raw_expectations:
        raise _fail(path, "expectations must be a non-empty array")

    root_parser_version = _optional_version(
        document.get("parser_version"), path, "parser_version"
    )
    _coordinate(document.get("start"), path, "start")
    root_end_line = _positive_integer(
        document.get("end_line"), path, "end_line"
    )
    root_end_offset = _positive_integer(
        document.get("end_offset"), path, "end_offset"
    )
    if root_end_offset is not None and root_end_line is None:
        raise _fail(path, "end_offset requires end_line")
    parsed_expectations = []
    ranges = []
    raw_expectations = sorted(
        raw_expectations,
        key=lambda item: (
            item.get("runtime_minimum") or [3, 0],
            item.get("runtime_maximum") or [3, 99],
        ),
    )
    for index, raw in enumerate(raw_expectations, start=1):
        if not isinstance(raw, dict):
            raise _fail(path, f"expectation {index} must be a table")
        unknown = set(raw) - EXPECTATION_KEYS
        if unknown:
            raise _fail(
                path, f"expectation {index} has unknown fields: {sorted(unknown)}"
            )
        runtime_minimum = _optional_version(
            raw.get("runtime_minimum"),
            path,
            f"expectation {index}.runtime_minimum",
        )
        runtime_maximum = _optional_version(
            raw.get("runtime_maximum"),
            path,
            f"expectation {index}.runtime_maximum",
        )
        if (
            runtime_minimum is not None
            and runtime_maximum is not None
            and runtime_minimum > runtime_maximum
        ):
            raise _fail(
                path,
                f"expectation {index} runtime_minimum must not exceed "
                "runtime_maximum",
            )
        if runtime_minimum is None and runtime_maximum is not None:
            runtime_minimum = (3, 10)
        if runtime_maximum is None and runtime_minimum is not None:
            runtime_maximum = (3, 15)
        for other_minimum, other_maximum in ranges:
            latest_start = runtime_minimum or (3, 0)
            if other_minimum is not None and other_minimum > latest_start:
                latest_start = other_minimum
            earliest_end = runtime_maximum or (3, 99)
            if other_maximum is not None and other_maximum < earliest_end:
                earliest_end = other_maximum
            if latest_start <= earliest_end:
                raise _fail(path, "expectation runtime ranges overlap")
        ranges.append((runtime_minimum, runtime_maximum))

        expectation_messages = raw.get("messages")
        messages = (
            root_messages
            if expectation_messages is None
            else _messages(
                expectation_messages, path, f"expectation {index}.messages"
            )
        )
        if not messages:
            raise _fail(path, f"expectation {index} has no messages")
        parser_version = _optional_version(
            raw.get("parser_version"),
            path,
            f"expectation {index}.parser_version",
        )
        if root_parser_version is not None and parser_version is not None:
            raise _fail(
                path,
                f"expectation {index} duplicates the root parser_version",
            )
        start = _coordinate(
            raw.get("start", document.get("start")),
            path,
            f"expectation {index}.start",
        )
        end_line = _positive_integer(
            raw.get("end_line", document.get("end_line")),
            path,
            f"expectation {index}.end_line",
        )
        end_offset = _positive_integer(
            raw.get("end_offset", document.get("end_offset")),
            path,
            f"expectation {index}.end_offset",
        )
        if end_offset is not None and end_line is None:
            raise _fail(path, f"expectation {index} end_offset requires end_line")
        parsed_expectations.append(
            (
                runtime_minimum,
                runtime_maximum,
                InvalidExpectation(
                    messages=messages,
                    parser_version=parser_version or root_parser_version,
                    start=start,
                    end_line=end_line,
                    end_offset=end_offset,
                ),
            )
        )

    normalized_expectations = []
    for minimum, maximum, expectation in parsed_expectations:
        if normalized_expectations:
            previous_minimum, previous_maximum, previous = normalized_expectations[-1]
            previous_end = previous_maximum or (3, 99)
            current_start = minimum or (3, 0)
            consecutive = current_start == (
                previous_end[0],
                previous_end[1] + 1,
            )
            if consecutive and previous == expectation:
                normalized_expectations[-1] = (
                    previous_minimum,
                    maximum or previous_maximum,
                    expectation,
                )
                continue
        normalized_expectations.append((minimum, maximum, expectation))
    parsed_expectations = normalized_expectations

    if len(parsed_expectations) > 1:
        current = (3, 10)
        for minimum, maximum, _expectation in parsed_expectations:
            if minimum is None:
                raise _fail(path, "runtime expectations must define coverage ranges")
            if minimum != current:
                raise _fail(
                    path,
                    f"runtime expectations leave a gap before Python {minimum[0]}."
                    f"{minimum[1]}",
                )
            current = (
                maximum[0],
                maximum[1] + 1,
            ) if maximum is not None else (3, 99)
        if current != (3, 16):
            raise _fail(
                path,
                "runtime expectations must cover Python 3.10 through 3.15",
            )

    return InvalidFixture(
        path=path,
        source=source,
        minimum_python=minimum_python,
        maximum_python=maximum_python,
        skip_reason=skip_reason,
        expectations=tuple(parsed_expectations),
    )


def _python_version():
    return sys.version_info[0], sys.version_info[1]


def pytest_generate_tests(metafunc):
    if "invalid_fixture_path" not in metafunc.fixturenames:
        return

    version = _python_version()
    parameters = []
    fixture_roots = (
        (PYTHON_INVALID_DIR, "*.py"),
        (ENAML_INVALID_DIR, "*.enaml"),
    )
    for fixture_root, pattern in fixture_roots:
        if not fixture_root.exists():
            continue
        for path in sorted(
            fixture_root.rglob(pattern),
            key=lambda path: path.relative_to(INVALID_ROOT).as_posix(),
        ):
            fixture = parse_invalid_fixture(path)
            fixture_id = path.relative_to(INVALID_ROOT).as_posix()
            if not fixture.is_supported(version):
                parameters.append(
                    pytest.param(
                        path,
                        marks=pytest.mark.skip(
                            fixture.skip_reason or "unsupported Python version"
                        ),
                        id=fixture_id,
                    )
                )
            else:
                fixture.select_expectation(version)
                parameters.append(pytest.param(path, id=fixture_id))
    metafunc.parametrize("invalid_fixture_path", parameters)


@pytest.fixture
def invalid_fixture_parser():
    return parse_invalid_fixture


@pytest.fixture
def invalid_fixture_format_error():
    return FixtureFormatError


@pytest.fixture
def invalid_fixture(invalid_fixture_path):
    return parse_invalid_fixture(invalid_fixture_path)
