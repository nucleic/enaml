async def f():
    a = [i async for i in range(10)]
    return a
