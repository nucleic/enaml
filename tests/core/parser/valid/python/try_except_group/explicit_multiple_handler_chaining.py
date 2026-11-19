orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* TypeError as e:
        raise SyntaxError(3) from e
    except* ValueError as e:
        raise SyntaxError(4) from e
except ExceptionGroup as e:
    exc = e

orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* TypeError:
        e = sys.exception()
        raise SyntaxError(3) from e
    except* ValueError:
        e = sys.exception()
        raise SyntaxError(4) from e
except ExceptionGroup as e:
    exc = e
