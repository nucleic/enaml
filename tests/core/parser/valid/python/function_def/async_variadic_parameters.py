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
