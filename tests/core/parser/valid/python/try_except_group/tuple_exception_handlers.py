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
