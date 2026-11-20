async def f():
    async for i in a:
        pass

    async for i, in a:
        pass

    async for (i,) in a:
        pass

    async for (i,), in a:
        pass

    async for i, *j in a:
        pass

    async for i, (a, *b) in a:
        pass
