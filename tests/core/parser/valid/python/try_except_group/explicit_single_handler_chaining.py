orig = ExceptionGroup("eg", [ValueError(1), OSError(2)])
try:
    try:
        raise orig
    except* OSError as e:
        raise TypeError(3) from e
except ExceptionGroup as e:
    exc = e

orig = ExceptionGroup("eg", [ValueError(1), OSError(2)])
try:
    try:
        raise orig
    except* OSError:
        e = sys.exception()
        raise TypeError(3) from e
except ExceptionGroup as e:
    exc = e
