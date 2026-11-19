orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* (TypeError, ValueError) as e:
        raise SyntaxError(3) from e
except SyntaxError as e:
    exc = e

orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* (TypeError, ValueError) as e:
        e = sys.exception()
        raise SyntaxError(3) from e
except SyntaxError as e:
    exc = e
