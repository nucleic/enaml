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



try:
    try:
        raise ValueError(42)
    except* ValueError as e:
        raise
except ExceptionGroup as e:
    exc = e



try:
    try:
        raise ValueError(42)
    except* ValueError:
        raise
except ExceptionGroup as e:
    exc = e



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



orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* (TypeError, ValueError) as e:
        raise SyntaxError(3)
except SyntaxError as e:
    exc = e



orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* (TypeError, ValueError) as e:
        raise SyntaxError(3)
except SyntaxError as e:
    exc = e



orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* TypeError as e:
        raise SyntaxError(3)
    except* ValueError as e:
        raise SyntaxError(4)
except ExceptionGroup as e:
    exc = e



orig = ExceptionGroup("eg", [TypeError(1), ValueError(2)])
try:
    try:
        raise orig
    except* TypeError:
        raise SyntaxError(3)
    except* ValueError:
        raise SyntaxError(4)
except ExceptionGroup as e:
    exc = e



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


