import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .downloader import VideoDownloader
from .stats import StatsManager
from .config import MAX_FILE_SIZE_MB

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

downloader = VideoDownloader()
stats_manager = StatsManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    stats_manager.track_user(user.id)
    await update.message.reply_html(
        f"Hi {user.mention_html()}! \n"
        "Send me a video URL and I will try to download it for you.\n"
        "Supported Command: \n"
        "/help - Show help message\n"
        "/stats - Show bot statistics"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send stats message."""
    stats = stats_manager.get_stats()
    await update.message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"👥 Unique Users: {stats['unique_users']}\n"
        f"⬇️ Total Downloads: {stats['total_downloads']}",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    await update.message.reply_text(
        "Simply send me a valid link from a supported video platform (YouTube, Twitter, Instagram, etc.).\n"
        "I will download it in 720p (or best available) and send it to you."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    message = update.message
    text = message.text

    if not text:
        return

    # Basic URL check
    if not text.startswith("http"):
        await message.reply_text("Please send a valid URL starting with http:// or https://")
        return

    status_msg = await message.reply_text("Fetching video info...")
    
    try:
        # Fetch info first
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, downloader.get_video_info, text)
        
        # Store URL in user_data context for retrieval in button callback
        context.user_data['download_url'] = text
        
        title = info.get('title', 'Video')
        
        # Create Inline Keyboard for Quality Selection
        keyboard = [
            [
                InlineKeyboardButton("1080p", callback_data="quality|1080"),
                InlineKeyboardButton("720p", callback_data="quality|720"),
            ],
            [
                InlineKeyboardButton("480p", callback_data="quality|480"),
                InlineKeyboardButton("Best Available", callback_data="quality|best"),
            ],
             [
                InlineKeyboardButton("Audio Only", callback_data="quality|audio"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await status_msg.edit_text(
            f"🎬 <b>{title}</b>\n\nSelect download quality:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error handling URL: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer() # Ack the callback

    data = query.data
    if not data.startswith("quality|"):
        return

    quality = data.split("|")[1]
    url = context.user_data.get('download_url')

    if not url:
        await query.edit_message_text("❌ Error: Download link expired or not found. Please send the link again.")
        return

    await query.edit_message_text(f"Queueing download for <b>{quality}</b>...", parse_mode='HTML')
    
    # Trigger download
    file_path = None
    try:
        loop = asyncio.get_running_loop()
        # Pass quality to downloader
        result = await loop.run_in_executor(None, downloader.download_video, url, quality)
        
        file_path = result['file_path']
        title = result['title']
        filesize = result['filesize']
        filesize_mb = filesize / (1024 * 1024)

        if filesize_mb > MAX_FILE_SIZE_MB:
            await query.edit_message_text(
                f"Video downloaded!\nTitle: {title}\n"
                f"Size: {filesize_mb:.2f} MB\n"
                "⚠️ File is large, uploading now..."
            )
        else:
            await query.edit_message_text("Uploading to Telegram...")

        # Send Video or Audio
        with open(file_path, 'rb') as f:
            if quality == 'audio':
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=f,
                    title=title,
                    caption=f"🎵 <b>{title}</b>",
                    parse_mode='HTML',
                    read_timeout=120,
                    write_timeout=120
                )
            else:
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=f,
                    caption=f"🎥 <b>{title}</b> ({quality})",
                    parse_mode='HTML',
                    supports_streaming=True,
                    read_timeout=120, 
                    write_timeout=120
                )
        
        # Increment stats
        stats_manager.increment_download()
        
        # Delete init message to clean up
        await query.delete_message()

    except Exception as e:
        logger.error(f"Error downloading: {e}")
        await query.message.reply_text(f"❌ Download failed: {str(e)}")
    
    finally:
         if file_path:
            downloader.cleanup(file_path)
