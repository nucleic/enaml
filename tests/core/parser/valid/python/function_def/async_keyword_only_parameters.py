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
