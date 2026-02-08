import logging
import sys
import os
import shutil
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.request import HTTPXRequest
from src.config import TOKEN, FFMPEG_PATH
from src.handlers import start, help_command, handle_message, button_handler, stats_command
from src.keep_alive import keep_alive

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Start health check server for Docker environments
    keep_alive()

    if not TOKEN or TOKEN == "your_token_here":
        logger.error("Error: BOT_TOKEN (or TELEGRAM_BOT_TOKEN) is not set.")
        sys.exit(1)

    if not shutil.which(str(FFMPEG_PATH)) and not os.path.exists(str(FFMPEG_PATH)):
        logger.warning(f"Warning: FFmpeg not found at {FFMPEG_PATH}. Video merging might fail or quality might be lower. Please install FFmpeg.")
    else:
        logger.info(f"FFmpeg found.")

    try:
        # Increase timeouts for large file uploads
        request = HTTPXRequest(connect_timeout=60, read_timeout=120, write_timeout=120, pool_timeout=120)
        application = ApplicationBuilder().token(TOKEN).request(request).build()

        start_handler = CommandHandler('start', start)
        help_handler = CommandHandler('help', help_command)
        stats_handler = CommandHandler('stats', stats_command)
        message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
        callback_handler = CallbackQueryHandler(button_handler)

        application.add_handler(start_handler)
        application.add_handler(help_handler)
        application.add_handler(stats_handler)
        application.add_handler(message_handler)
        application.add_handler(callback_handler)

        logger.info("Bot is starting...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
