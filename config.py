from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file if present

# Telegram API credentials
API_ID = int(os.getenv("API_ID", "21519702"))
API_HASH = os.getenv("API_HASH", "20fcf051ad48130f35fe01e82f5417cd")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7976010249:AAHX1GvKqNOuUq2QxOBqgOtzYs7yabD6l00")

# Download settings
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/sdcard/YTDownload1")
COOKIES_FILE = os.getenv("COOKIES_FILE", "/sdcard/YTDownload1/cookies.txt")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "/data/data/com.termux/files/usr/bin/ffmpeg")
