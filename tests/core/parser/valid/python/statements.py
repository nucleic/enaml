if value > 0:
    result = "positive"
else:
    result = "non-positive"

for item in range(3):
    result = item

try:
    raise ValueError("demo")
except ValueError as exc:
    result = str(exc)


def compute():
    if value > 0:
        return value
    return None


def generate():
    yield value
    yield from range(3)
