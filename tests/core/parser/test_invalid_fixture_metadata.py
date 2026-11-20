from pathlib import Path
import re

import pytest

def write_fixture(tmp_path: Path, header: str, source: str = "bad source\n") -> Path:
    path = tmp_path / "invalid.py"
    path.write_text(
        f"{header}"
        "# --- source ---\n"
        f"{source}",
        encoding="utf-8",
    )
    return path


def test_fixture_source_is_preserved_exactly(tmp_path, invalid_fixture_parser):
    path = write_fixture(
        tmp_path,
        '# messages = ["invalid syntax"]\n',
        "\n  invalid syntax\n",
    )

    fixture = invalid_fixture_parser(path)

    assert fixture.source == "\n  invalid syntax\n"


@pytest.mark.parametrize(
    "header",
    [
        "# messages = []\n",
        "# unexpected = true\n"
        '# messages = ["invalid syntax"]\n',
        '# messages = ["invalid syntax"]\n'
        "# end_offset = 2\n",
        "# expectations = [\n"
        "#   { runtime_minimum = [3, 12], messages = [\"old\"] },\n"
        "#   { runtime_maximum = [3, 13], messages = [\"new\"] }\n"
        "# ]\n",
    ],
)
def test_invalid_metadata_is_rejected(
    tmp_path, header, invalid_fixture_parser, invalid_fixture_format_error
):
    with pytest.raises(invalid_fixture_format_error):
        invalid_fixture_parser(write_fixture(tmp_path, header))


def test_expectation_inherits_messages_and_parser_version(
    tmp_path, invalid_fixture_parser
):
    path = write_fixture(
        tmp_path,
        '# messages = ["invalid syntax"]\n'
        "# parser_version = [3, 10]\n"
    )

    expectation = invalid_fixture_parser(path).select_expectation((3, 12))

    assert expectation.messages == ("invalid syntax",)
    assert expectation.parser_version == (3, 10)


def test_partial_end_location_is_preserved(tmp_path, invalid_fixture_parser):
    path = write_fixture(
        tmp_path,
        '# messages = ["invalid syntax"]\n'
        "# end_line = 2\n",
    )

    expectation = invalid_fixture_parser(path).select_expectation((3, 12))

    assert expectation.end_line == 2
    assert expectation.end_offset is None


def test_fixture_requires_exactly_one_active_expectation(
    tmp_path, invalid_fixture_parser
):
    path = write_fixture(
        tmp_path,
        "# expectations = [\n"
        "#   { runtime_maximum = [3, 11], messages = [\"old\"] },\n"
        "#   { runtime_minimum = [3, 12], messages = [\"new\"] }\n"
        "# ]\n",
    )

    fixture = invalid_fixture_parser(path)

    assert fixture.select_expectation((3, 11)).messages == ("old",)
    assert fixture.select_expectation((3, 12)).messages == ("new",)


@pytest.mark.parametrize(
    "expectations",
    [
        "# expectations = [\n"
        "#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], "
        'messages = ["old"] },\n'
        "#   { runtime_minimum = [3, 13], runtime_maximum = [3, 15], "
        'messages = ["new"] }\n'
        "# ]\n",
        "# expectations = [\n"
        "#   { runtime_minimum = [3, 10], runtime_maximum = [3, 12], "
        'messages = ["old"] },\n'
        "#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], "
        'messages = ["new"] }\n'
        "# ]\n",
    ],
)
def test_runtime_ranges_must_be_complete_and_non_overlapping(
    tmp_path, expectations, invalid_fixture_parser, invalid_fixture_format_error
):
    with pytest.raises(invalid_fixture_format_error):
        invalid_fixture_parser(write_fixture(tmp_path, expectations))


def test_invalid_fixture_names_do_not_use_migration_ordinals(invalid_fixture_parser):
    invalid_dir = Path(__file__).resolve().parent / "invalid" / "python"
    numbered = [
        path.relative_to(invalid_dir).as_posix()
        for path in invalid_dir.rglob("*.py")
        if re.match(r"^\d+_", path.name)
    ]

    assert not numbered


def test_invalid_fixture_sources_are_unique(invalid_fixture_parser):
    invalid_dir = Path(__file__).resolve().parent / "invalid" / "python"
    sources = {}
    duplicates = []
    for path in invalid_dir.rglob("*.py"):
        fixture = invalid_fixture_parser(path)
        if fixture.source in sources:
            duplicates.append(
                (sources[fixture.source], path.relative_to(invalid_dir).as_posix())
            )
        else:
            sources[fixture.source] = path.relative_to(invalid_dir).as_posix()

    assert not duplicates

