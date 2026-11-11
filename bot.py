import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream
import yt_dlp

# Replace with your actual credentials or use environment variables
API_ID = "YOUR_API_ID" 
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Initialize the Pyrogram client
app = Client(
    "music_bot",
    api_id="38587651",
    api_hash="d054a6ae5ae2a1ad8244785717721644",
    bot_token="9250047337:AAENjgzbYlqlcm8LvaiDsSQuJH3we5sdq5E"
)

# Initialize PyTgCalls
call_py = PyTgCalls(app)

# Helper function to extract audio URL from YouTube
def get_audio_url(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

@app.on_message(filters.command("play") & filters.group)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide a YouTube link. Usage: /play [link]")
        return

    youtube_url = message.command[1]
    chat_id = message.chat.id

    status_msg = await message.reply("⏳ Fetching audio stream...")

    try:
        # Extract the direct audio stream URL
        audio_url = get_audio_url(youtube_url)

        # Join the voice chat and stream the audio
        await call_py.play(
            chat_id,
            MediaStream(audio_url)
        )
        await status_msg.edit_text("▶️ Playing music in the Voice Chat!")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error playing music: {e}")

# Start the clients and idle
async def main():
    await app.start()
    await call_py.start()
    print("Bot is running and ready to play music!")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())