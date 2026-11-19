async def g():
    async with a:
        pass

    async with a, b:
        pass

    async with a as b:
        pass

    async with a as b, c:
        pass
