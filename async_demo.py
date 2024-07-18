import asyncio
import aiohttp
def get_tasks(session):
    task = []
    for symbol in ["AAPL", "GOOGL", "MSFT"]:
        task.append(session.get(url.format(symbol, api_key), ssl=False)
    return tasks

async def ge_symbols():
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(await response.json())