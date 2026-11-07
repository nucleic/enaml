def add(left, right=0):
    return left + right


def outer(name):
    def inner(value):
        return f"{name}:{value}"

    return inner
