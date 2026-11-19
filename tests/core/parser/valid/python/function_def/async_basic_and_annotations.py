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
