import aiohttp

session: aiohttp.ClientSession = None

async def get_client():
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    return session

async def close_client():
    global session
    if session and not session.closed:
        await session.close()
