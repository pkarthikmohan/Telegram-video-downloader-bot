from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import threading
import logging

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Telegram Video Downloader Bot is running!")

    def log_message(self, format, *args):
        pass # Silence server logs

def start_server():
    try:
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"Health check server listening on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health check server: {e}")

def keep_alive():
    t = threading.Thread(target=start_server)
    t.daemon = True # Dies when main thread dies
    t.start()
