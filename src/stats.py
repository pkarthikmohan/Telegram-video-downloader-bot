import json
import os
import logging
import random

logger = logging.getLogger(__name__)

STATS_FILE = os.path.join(os.getcwd(), 'stats.json')

class StatsManager:
    def __init__(self):
        self.stats = self._load_stats()
        # Seed logic: If users/downloads are low, set high fake baselines
        if len(self.stats["users"]) < 5000:
             self.stats["users"] = list(range(98421)) # Fake user count by list length
             # Assume ~7 downloads per user on average
             self.stats["total_downloads"] = random.randint(650000, 750000) 
             self._save_stats()

    def _load_stats(self):
        if not os.path.exists(STATS_FILE):
             # Cold start values
            fake_users = list(range(98421))
            fake_downloads = random.randint(650000, 750000)
            return {"users": fake_users, "total_downloads": fake_downloads}
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load stats: {e}")
            # Fallback
            return {"users": list(range(98421)), "total_downloads": 700000}

    def _save_stats(self):
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def track_user(self, user_id):
        if user_id not in self.stats["users"]:
            self.stats["users"].append(user_id)
            self._save_stats()

    def increment_download(self):
        self.stats["total_downloads"] += 1
        self._save_stats()

    def get_stats(self):
        return {
            "unique_users": len(self.stats["users"]),
            "total_downloads": self.stats["total_downloads"]
        }
