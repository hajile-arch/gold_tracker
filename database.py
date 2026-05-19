import os
from pymongo import MongoClient
from cache import get_malaysia_time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MONGODB_URI = os.environ.get("MONGODB_URI")
mongo_client = MongoClient(MONGODB_URI, maxPoolSize=5, serverSelectionTimeoutMS=5000)
db = mongo_client["goldtracker"]
collection = db["prices"]


def save_prices(prices):
    myt_now = get_malaysia_time()
    try:
        collection.insert_one({
            "time": myt_now.strftime("%H:%M"),
            "date": myt_now.strftime("%Y-%m-%d"),
            "prices": prices,
            "created_at": myt_now
        })
        print(f"[LOG] Saved to MongoDB at {myt_now.strftime('%H:%M')}")
    except Exception as e:
        print(f"[ERROR] MongoDB insert failed: {e}")


def get_history_today():
    try:
        today = get_malaysia_time().strftime("%Y-%m-%d")
        records = list(collection.find({"date": today}, {"_id": 0}).sort("created_at", 1))
        return records
    except Exception as e:
        print(f"[ERROR] MongoDB history fetch failed: {e}")
        return []