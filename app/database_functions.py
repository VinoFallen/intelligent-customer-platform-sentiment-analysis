from pymongo import MongoClient
from datetime import datetime
from dateutil import parser as date_parser
import re
import dotenv, os

# MongoDB URI
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)

db = client["sentiment_db"]


def email_entry(info_dict):
    if not info_dict or not isinstance(info_dict, dict):
        print("Invalid info_dict received:", info_dict)
        return False

    try:
        # --- Extract fields ---
        e_id = info_dict.get('id')
        sender = info_dict.get('sender')
        subject = info_dict.get('subject')
        body = info_dict.get('body')
        timestamp = info_dict.get('timestamp')
        sentiment_score = 0.0
        sentiment_category = "None"

        # --- Extract sender name and email ---
        if isinstance(sender, str):
            match = re.match(r'(.+?)\s*<(.+?)>', sender)
            if match:
                sender_name = match.group(1)
                sender_mail = match.group(2)
            else:
                sender_name = ''
                sender_mail = sender  # fallback
        else:
            sender_name = ''
            sender_mail = ''

        # --- Convert timestamp to date and time ---
        if timestamp is not None:
            dt = date_parser.parse(timestamp)
            date = dt.strftime("%Y-%m-%d")
            time = dt.strftime("%H:%M:%S")
        else:
            date = ""
            time = ""

        # --- Check for collection ---
        collection_name = sender_mail
        collection_names = db.list_collection_names()

        collection = db[collection_name]

        if collection_name not in collection_names:
            collection.insert_one({
                "sender_name": sender_name
            })

        if collection.find_one({"_id": e_id}):
            print(f"Duplicate entry with _id {e_id} already exists. Skipping insertion.")
        else:
            collection.insert_one({
                "_id": e_id,
                "subject": subject,
                "body": body,
                "sentiment_score": sentiment_score,
                "sentiment_category": sentiment_category,
                "date": date,
                "time": time
            })
            print(f"Entry added to collection '{collection_name}' with _id {e_id}.")


        return True 

    except Exception as e:
        print(f"Error occurred: {e}")
        return False  




