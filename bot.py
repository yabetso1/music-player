import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream
import yt_dlp
from aiohttp import web

API_ID = "38587651" 
API_HASH = "d054a6ae5ae2a1ad8244785717721644"
BOT_TOKEN = "9250047337:AAENjgzbYlqlcm8LvaiDsSQuJH3we5sdq5E"

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

def get_audio_url(query):
    # Tell yt-dlp to search SoundCloud instead of YouTube
    if not query.startswith("http"):
        query = f"scsearch:{query}"
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:  # Grab the first track from the search results
            info = info['entries'][0]
        return info['url']

@app.on_message(filters.command("play") & filters.group)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide a song name or link. Usage: /play [song name]")
        return

    # Combine all text after /play so users can search phrases with spaces
    query = " ".join(message.command[1:])
    chat_id = message.chat.id

    status_msg = await message.reply(f"⏳ Searching for '{query}'...")

    try:
        audio_url = get_audio_url(query)
        await call_py.play(chat_id, MediaStream(audio_url))
        await status_msg.edit_text(f"▶️ Playing: {query}")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error playing music: {e}")

# Dummy Web Server to prevent Render from shutting down the bot
async def web_server():
    async def handle(request):
        return web.Response(text="Bot is healthy!")
    web_app = web.Application()
    web_app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    # Bind to Render's assigned port
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await web_server() # Start the web server in the background
    await app.start()
    await call_py.start()
    print("Bot is running and ready to play music!")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
