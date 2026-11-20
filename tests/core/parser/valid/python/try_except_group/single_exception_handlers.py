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
