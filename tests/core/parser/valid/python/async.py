async def fetch(query):
    return await query()


async def gather(items):
    result = []
    async for item in items:
        result.append(item)
    return result
