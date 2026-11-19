try:
    try:
        raise ExceptionGroup(
            "eg", [TypeError(1), ValueError(2), OSError(3)])
    except* TypeError as e:
        raise
    except* ValueError as e:
        raise
    # OSError not handled
except ExceptionGroup as e:
    exc = e

try:
    try:
        raise ExceptionGroup(
            "eg", [TypeError(1), ValueError(2), OSError(3)])
    except* TypeError:
        raise
    except* ValueError:
        raise
    # OSError not handled
except ExceptionGroup as e:
    exc = e

try:
    try:
        raise ExceptionGroup(
            "eg", [TypeError(1), ValueError(2), OSError(3)])
    except* TypeError as e:
        raise
    except* ValueError as e:
        pass
    # OSError not handled
except ExceptionGroup as e:
    exc = e

try:
    try:
        raise ExceptionGroup(
            "eg", [TypeError(1), ValueError(2)])
    except* TypeError:
        raise
    except* ValueError:
        pass
except ExceptionGroup as e:
    exc = e

try:
    try:
        raise ExceptionGroup(
            "eg", [TypeError(1), ValueError(2), OSError(3)])
    except* TypeError as e:
        raise
    except* ValueError as e:
        pass
    # OSError not handled
except ExceptionGroup as e:
    exc = e

try:
    try:
        raise ExceptionGroup(
            "eg", [TypeError(1), ValueError(2), OSError(3)])
    except* TypeError:
        raise
    except* ValueError:
        pass
except ExceptionGroup as e:
    exc = e
