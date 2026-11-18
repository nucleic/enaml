a = 1  # type: int

for i in range(10):  # type: int
    pass


with a:  # type: int
    pass


def f(a): # type: (int) -> None
    pass


def f(a):
    # type: (int) -> None
    pass
