import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in .env file")

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf",".txt"}
