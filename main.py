import logging
import sys
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from src.config import TOKEN, FFMPEG_PATH
from src.handlers import start, help_command, handle_message, button_handler, stats_command

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    if not TOKEN or TOKEN == "your_token_here":
        logger.error("Error: TELEGRAM_BOT_TOKEN is not set in .env file.")
        sys.exit(1)

    if not os.path.exists(FFMPEG_PATH):
        logger.warning(f"Warning: FFmpeg not found at {FFMPEG_PATH}. Video merging might fail or quality might be lower. Please install FFmpeg or ensure the binaries are in the bot root folder.")
    else:
        logger.info(f"FFmpeg found at: {FFMPEG_PATH}")

    try:
        application = ApplicationBuilder().token(TOKEN).build()

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
