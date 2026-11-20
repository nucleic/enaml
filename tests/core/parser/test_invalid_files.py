import io
import sys
import tokenize

import pytest

from enaml.core.parser import parse


def test_invalid_fixtures_raise_matching_syntax_error(invalid_fixture):
    fixture_id = invalid_fixture.fixture_id
    expectation = invalid_fixture.select_expectation(
        (sys.version_info[0], sys.version_info[1])
    )

    with pytest.raises(SyntaxError) as exc:
        parse(
            invalid_fixture.source,
            py_version=expectation.parser_version,
        )

    error = exc.value
    text = str(error)
    if not any(message.lower() in text.lower() for message in expectation.messages):
        tokens = list(
            tokenize.generate_tokens(io.StringIO(invalid_fixture.source).readline)
        )
        pytest.fail(
            f"{fixture_id}: no expected message matched {text!r}\n"
            f"accepted={expectation.messages!r}\n"
            f"source={invalid_fixture.source!r}\n"
            f"tokens={tokens!r}"
        )

    if expectation.start is not None:
        assert (error.lineno, error.offset) == expectation.start
    if expectation.end_line is not None:
        assert getattr(error, "end_lineno", None) == expectation.end_line
    if expectation.end_offset is not None:
        assert getattr(error, "end_offset", None) == expectation.end_offset

