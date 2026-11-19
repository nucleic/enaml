orig = ExceptionGroup("eg", [ValueError(1), OSError(2)])
try:
    try:
        raise orig
    except* OSError as e:
        raise TypeError(3)
except ExceptionGroup as e:
    exc = e

orig = ExceptionGroup("eg", [ValueError(1), OSError(2)])
try:
    try:
        raise orig
    except* OSError:
        raise TypeError(3)
except ExceptionGroup as e:
    exc = e
