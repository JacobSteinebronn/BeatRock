import httpx
import asyncio
import uuid

client = httpx.AsyncClient()

async def main():
    data = {"prev": "rock", "guess": "paper", "gid": str(uuid.uuid4())}
    headers = {"User-Agent": "@meaf, on discord"}
    resp = await client.post("https://www.whatbeatsrock.com/api/vs", json=data, headers=headers)
    print(resp.status_code)
    print(resp.json())

asyncio.run(main())
    