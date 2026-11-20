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
