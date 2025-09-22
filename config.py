from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file if present

# Telegram API credentials
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Download settings
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/sdcard/YTDownload1")
COOKIES_FILE = os.getenv("COOKIES_FILE", f"{DOWNLOAD_DIR}/cookies.txt")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "/data/data/com.termux/files/usr/bin/ffmpeg")
