import asyncio
from pyrogram import Client

API_ID = "38587651"
API_HASH = "d054a6ae5ae2a1ad8244785717721644"

async def main():
    async with Client("my_account", api_id=API_ID, api_hash=API_HASH, in_memory=True) as app:
        print("\n--- YOUR STRING SESSION ---")
        print(await app.export_session_string())
        print("---------------------------\n")

asyncio.run(main())