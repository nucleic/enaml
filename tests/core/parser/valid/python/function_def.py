def f():
    pass


def f() -> None:
    pass


def f(a):
    pass


def f(a: int) -> Tuple[int, ...]:
    pass


def f(a: int = 1) -> Tuple[int, ...]:
    pass


def f(a, b: int):
    pass


def f(a: bool, b: int = 1):
    pass


def f(a, /):
    pass


def f(a=1, /):
    pass


def f(a, b=1, /):
    pass


def f(a, /, b):
    pass


def f(a, c=2, /, b=5):
    pass


def f(a, /, b=1):
    pass


def f(a, *, b):
    pass


def f(a, *, b, c=1):
    pass


def f(a, *, b=1):
    pass


def f(*, b):
    pass


def f(*, b, c=1):
    pass


def f(*, b=1):
    pass


def f(b=1, *c):
    pass


def f(*args):
    pass


def f(**kwargs):
    pass


def f(a, **kwargs):
    pass


def f(a=1, **kwargs):
    pass


def f(*, a=1, **kwargs):
    pass


def f(*a, **b):
    pass


def f(a, /, b, *, v=1, **d):
    pass


async def f():
    pass


async def f() -> None:
    pass


async def f(a):
    pass


async def f(a: int) -> Tuple[int, ...]:
    pass


async def f(a: int = 1) -> Tuple[int, ...]:
    pass


async def f(a, b: int):
    pass


async def f(a: bool, b: int = 1):
    pass


async def f(a, /):
    pass


async def f(a=1, /):
    pass


async def f(a, b=1, /):
    pass


async def f(a, /, b):
    pass


async def f(a, c=2, /, b=5):
    pass


async def f(a, /, b=1):
    pass


async def f(a, *, b):
    pass


async def f(a, *, b=1):
    pass


async def f(*, b):
    pass


async def f(*, b=1):
    pass


async def f(b=1, *c):
    pass


async def f(*args):
    pass


async def f(**kwargs):
    pass


async def f(a, **kwargs):
    pass


async def f(a=1, **kwargs):
    pass


async def f(*, a=1, **kwargs):
    pass


async def f(*a, **b):
    pass


async def f(a, /, b, *, v=1, **d):
    pass
