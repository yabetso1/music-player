import os
import asyncio

# 1. Create the event loop FIRST to prevent the Python 3.14+ import error
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# 2. Now it is safe to import Pyrogram and PyTgCalls
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream
import yt_dlp
from aiohttp import web

# --- CREDENTIALS ---
API_ID = "38587651"       # Replace with your API ID (number, no quotes if it's an int, or string)
API_HASH = "d054a6ae5ae2a1ad8244785717721644"   # Replace with your API Hash
BOT_TOKEN = "9250047337:AAENjgzbYlqlcm8LvaiDsSQuJH3we5sdq5E" # Replace with your Bot Token

# The session string from your terminal
SESSION_STRING = "BAJMzQMApyRDGhzCtnLiJmA9Y9vi7DikAYQDvGWjUCGbi4-l_34vjwc-cpDyfB5NiEujCmTM7koMAjCNJ4bP94EOPfddrW7HtRdB7EWXJprSqdIswVJT7gw99UcneHXtP6haOH_2iJMjtML4JqEvxtwoihva8bsxqdyBqEn2StmqPEM3Kv3X_DTL8-F1fvp2rFGkvPc8Hk8hd5VdgC600IiB-7B-zTuTvDt8akAYVLafBw-9FHqBVMF-pYaHYYeKuPrM7u9ZS7Ojh0Md-rEvvyJ_bZc-0xCYmuCCGi-M_WE88TmUdYfGNpzFBerhgAXjFHJiF1y2gxRA6ePh0hauDDUhZ3OZnAAAAAAAYF8XpAA"

# --- CLIENT INITIALIZATION ---
# The Bot (Receives the commands in the text chat)
bot_app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# The Userbot (The invisible account that joins the voice chat)
user_app = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# Bind the music player to the Userbot
call_py = PyTgCalls(user_app)

# --- AUDIO SEARCH FUNCTION ---
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
        if 'entries' in info:
            info = info['entries'][0]
        return info['url']

# --- BOT COMMANDS ---
@bot_app.on_message(filters.command("play") & filters.group)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide a song name or link. Usage: /play [song name]")
        return

    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    status_msg = await message.reply(f"⏳ Searching for '{query}'...")

    try:
        audio_url = get_audio_url(query)
        await call_py.play(chat_id, MediaStream(audio_url))
        await status_msg.edit_text(f"▶️ Playing: {query}")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error playing music: {e}")

# --- RENDER WEB SERVER ---
async def web_server():
    async def handle(request):
        return web.Response(text="Bot is healthy!")
    web_app = web.Application()
    web_app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- MAIN LOOP ---
async def main():
    await web_server()
    await bot_app.start()
    await user_app.start()
    await call_py.start()
    print("Bot and Userbot are both running!")
    await idle()

if __name__ == "__main__":
    # Use the loop we manually created at the top
    loop.run_until_complete(main())