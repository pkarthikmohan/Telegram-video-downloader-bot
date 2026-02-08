import os
from dotenv import load_dotenv

# Load environment variables from the project root .env file
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# FFmpeg path
FFMPEG_PATH = os.getenv('FFMPEG_PATH') or 'ffmpeg'

# Max file size for Telegram local send is 50MB (standard) or 2GB (premium). 
# We'll set a safe limit for the bot to try and send directly.
MAX_FILE_SIZE_MB = 50 
