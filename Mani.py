import os
import asyncio
from uuid import uuid4

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_DIR, COOKIES_FILE, FFMPEG_PATH

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Initialize Pyrogram bot
app = Client("yt_upload_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary in-memory store for download requests
download_requests = {}  # format: {uuid: url}


# --- DOWNLOAD FUNCTION ---
async def download_youtube(url: str, quality: str = "1080p") -> tuple[str, str]:
    quality_map = {"1080p": 1080, "2k": 1440, "4k": 2160}
    max_height = quality_map.get(quality, 1080)

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "format": f"bestvideo[height<={max_height}]+bestaudio/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": FFMPEG_PATH,
        "noplaylist": True,
        "quiet": True
    }

    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).extract_info(url, download=True))
    file_path = YoutubeDL(ydl_opts).prepare_filename(info)
    title = info.get("title", "Video")
    return file_path, title


# --- HANDLER: Ask for quality ---
@app.on_message(filters.command("download") & filters.private)
async def download_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Send the YouTube URL like:\n`/download <youtube_url>`")
        return

    url = message.command[1]
    uid = str(uuid4())
    download_requests[uid] = url

    buttons = [
        [InlineKeyboardButton("1080p", callback_data=f"dl|{uid}|1080p")],
        [InlineKeyboardButton("2k", callback_data=f"dl|{uid}|2k")],
        [InlineKeyboardButton("4k", callback_data=f"dl|{uid}|4k")]
    ]

    await message.reply_text("🎥 Choose video quality:", reply_markup=InlineKeyboardMarkup(buttons))


# --- CALLBACK HANDLER: Process quality ---
@app.on_callback_query(filters.regex(r"^dl\|"))
async def callback_handler(client: Client, callback: CallbackQuery):
    try:
        _, uid, quality = callback.data.split("|")
        url = download_requests.get(uid)

        if not url:
            await callback.message.edit_text("❌ Session expired or invalid request.")
            return

        del download_requests[uid]

        msg = await callback.message.edit_text(f"⏳ Downloading video in {quality}...")
        file_path, title = await download_youtube(url, quality)
        await msg.edit_text("✅ Uploading video to Telegram...")

        file_size = os.path.getsize(file_path)
        max_size = 2 * 1024 * 1024 * 1024  # 2GB limit

        if file_size > max_size:
            await msg.edit_text("⚠️ File is too large for Telegram. Please try a lower quality.")
            os.remove(file_path)
            return

        await client.send_video(
            chat_id=callback.message.chat.id,
            video=file_path,
            caption=title,
            supports_streaming=True,
            progress=progress_callback,
            progress_args=(msg,)
        )

        await msg.delete()
        os.remove(file_path)

    except Exception as e:
        await callback.message.edit_text(f"❌ Error: {e}")


# --- Progress callback ---
async def progress_callback(current, total, message):
    try:
        percent = (current / total) * 100
        await message.edit_text(f"📤 Uploading: {percent:.1f}%")
    except:
        pass


# --- Command to check cookies ---
@app.on_message(filters.command("check_cookies") & filters.private)
async def check_cookies_handler(client: Client, message: Message):
    if os.path.exists(COOKIES_FILE):
        await message.reply_text("✅ Cookies file exists and will be used for downloads.")
    else:
        await message.reply_text("❌ Cookies file not found. Some videos might not be accessible.")


# --- RUN BOT ---
print("Bot is running...")
app.run()
