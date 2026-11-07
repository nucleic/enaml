import pytest

from enaml.core.parser import parse


@pytest.mark.parametrize(
    "source, message",
    [
        ("(a 1)", "invalid syntax"),
        ("print 1", "Missing parentheses"),
        ("a if b", "expected 'else'"),
        ("f'{x!}'", "missing conversion"),
        ("(a = 1)", "invalid syntax"),
    ],
)
def test_invalid_python_syntax_is_rejected(source, message):
    with pytest.raises(SyntaxError) as exc:
        parse(source)

    text = str(exc.value)
    assert message.lower() in text.lower()


@pytest.mark.parametrize(
    "source, message",
    [
        ("x = f'{x!q}'", "invalid conversion"),
        (
            "match x:\n    case 0:\n        pass\n    case _ as y:\n        pass",
            "cannot use '_' as a target",
        ),
    ],
)
def test_version_sensitive_invalid_syntax_is_rejected(source, message):
    with pytest.raises(SyntaxError) as exc:
        parse(source)

    text = str(exc.value)
    assert message.lower() in text.lower()
