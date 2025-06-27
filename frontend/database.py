# /frontend/database.py 

from pymongo import MongoClient
from datetime import datetime
import os 
from dotenv import load_dotenv
# MongoDB setup
load_dotenv()

uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client['sentiment_db']

def get_all_users():
    """Returns a list of users as {'email': ..., 'name': ...} from MongoDB."""
    all_collections = db.list_collection_names()
    users = [
        {"email": email, "name": email.split('@')[0]}
        for email in all_collections
        if not email.endswith("_trend")
    ]
    return users

def get_sentiment_trend(email):
    """Returns sentiment scores over time from <email>_trend collection."""
    collection_name = email + "_trend"
    if collection_name not in db.list_collection_names():
        return []

    results = db[collection_name].find({}, {
        "_id": 0,
        "timestamp": 1,
        "sentiment_score": 1,
        "subject": 1
    })

    data = [
        {
            "datetime": str(r["timestamp"]),  # stored as string like '2025-06-24 13:05:00'
            "score": r["sentiment_score"],
            "subject": r.get("subject", "No Subject")
        }
        for r in results
        if "timestamp" in r and "sentiment_score" in r
    ]
    data.sort(key=lambda x: x["datetime"])
    return data

def get_sentiment_details(email, datetime_str):
    """
    Returns summary, subject, sentiment_score, and action for a given timestamp string.
    Assumes datetime_str is stored exactly as 'YYYY-MM-DD HH:MM:SS' (string format).
    """
    collection = db[email]

    result = collection.find_one({
        "timestamp": datetime_str
    }, {
        "_id": 0,
        "subject": 1,
        "sentiment_score": 1,
        "summary": 1,
        "action": 1
    })

    return result