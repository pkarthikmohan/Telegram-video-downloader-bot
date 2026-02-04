import os
import uuid
import logging
import yt_dlp
from .config import DOWNLOAD_DIR, FFMPEG_PATH

logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self):
        self.download_path = DOWNLOAD_DIR
        self.ffmpeg_location = os.path.dirname(FFMPEG_PATH) if os.path.exists(FFMPEG_PATH) else None

    def get_video_info(self, url: str) -> dict:
        """Fetch video metadata without downloading."""
        ydl_opts = {
            'noplaylist': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                    'id': info.get('id')
                }
            except Exception as e:
                logger.error(f"Error fetching info: {e}")
                raise

    def download_video(self, url: str, quality: str = '720') -> dict:
        """
        Downloads a video from a given URL using yt-dlp.
        
        Args:
            url (str): The URL of the video to download.
            quality (str): Target resolution (e.g., '1080', '720', '480', 'best').

        Returns:
            dict: Dictionary containing 'file_path', 'title', 'duration', etc.
        """
        # Generate a unique filename to avoid collisions
        unique_id = str(uuid.uuid4())
        output_template = os.path.join(self.download_path, f'{unique_id}.%(ext)s')

        # Determine format string based on quality
        if quality == 'best':
            format_str = 'bestvideo+bestaudio/best'
        elif quality == 'audio':
             format_str = 'bestaudio/best'
        else:
            # Try to get best video <= target height, fallback to next best
            format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'

        # yt-dlp options
        ydl_opts = {
            'format': format_str,
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'max_filesize': 2000 * 1024 * 1024, # Limit download to 2GB max
            'ffmpeg_location': self.ffmpeg_location,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 1. Extract info to validate and get metadata
                info = ydl.extract_info(url, download=False)
                
                # 2. Download
                # Note: valid URL is checked by extract_info
                logger.info(f"Starting download for: {url}")
                error_code = ydl.download([url])
                
                if error_code != 0:
                    raise Exception("Download failed with error code")
                
                # Find the downloaded file
                # prepare_filename might not include the extension correct after merge, 
                # so we search for the file with the uuid in the dir
                downloaded_file = None
                for filename in os.listdir(self.download_path):
                    if unique_id in filename:
                        downloaded_file = os.path.join(self.download_path, filename)
                        break
                
                if not downloaded_file:
                    raise Exception("Downloaded file not found.")

                return {
                    'file_path': downloaded_file,
                    'title': info.get('title', 'Video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'filesize': os.path.getsize(downloaded_file)
                }

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Download error: {e}")
            raise Exception(f"Failed to download video: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"An error occurred: {str(e)}")

    def cleanup(self, file_path: str):
        """Removes the temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to clean up file {file_path}: {e}")
