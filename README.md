# Telegram Video Downloader Bot

A Python-based Telegram bot that downloads videos from various supported platforms (YouTube, Twitter, Instagram, etc.) using `yt-dlp` and sends them back to the user.

## Features

-   **Wide Support**: Downloads from any site supported by `yt-dlp`.
-   **Quality**: Attempts to download the best quality up to 720p.
-   **Privacy**: No permanent storage of user data or videos; files are deleted after sending.
-   **Validation**: Basic URL validation and size checks.

## usage

1.  **Clone/Download** this repository.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You also need ffmpeg installed on your system path for video merging.*
3.  **Configuration**:
    -   Rename `.env.example` to `.env`.
    -   Open `.env` and paste your Telegram Bot Token obtained from @BotFather.
4.  **Run**:
    ```bash
    python main.py
    ```
5.  **Interact**:
    -   Start a chat with your bot on Telegram.
    -   Send a link (e.g., a YouTube video).
    -   The bot will download and send the video file.

## Requirements

-   Python 3.8+
-   ffmpeg (must be in system PATH)
