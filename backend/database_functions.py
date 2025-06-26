#/backend/database_functions.py

from pymongo import MongoClient
from datetime import datetime
from dateutil import parser as date_parser
import re
import dotenv
import os
from api_client import analyze_sentiment_and_summary

dotenv.load_dotenv()
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
        if timestamp:
            dt = date_parser.parse(timestamp)
            date = dt.strftime("%Y-%m-%d")
            time = dt.strftime("%H:%M:%S")
        else:
            date = ""
            time = ""

        # --- Get prediction and summary from Hugging Face inference API ---
        response = analyze_sentiment_and_summary(str(body))

        sentiment_category = response.get("label", "None")
        sentiment_score = {
            "Positive": 2,
            "Negative": -3,
            "Neutral (General)": 1,
            "Neutral (Action-Oriented)": 0.5
        }.get(sentiment_category, 0)

        summary_of_email = response.get("Summary", "")
        bestCourseOfAction = response.get("Best Course of Action", "")

        # --- Prepare MongoDB collection ---
        collection_name = sender_mail
        collection_names = db.list_collection_names()
        collection = db[collection_name]
        is_new_collection = collection_name not in collection_names

        # --- Insert metadata if new sender ---
        if is_new_collection:
            collection.insert_one({
                "_id": "metadata",
                "sender_name": sender_name,
                "total_sentiment": sentiment_score
            })

        # --- Avoid duplicate email insertions ---
        if collection.find_one({"_id": e_id}):
            print(f"Duplicate entry with _id {e_id} already exists. Skipping insertion.")
        else:
            # Insert new email
            collection.insert_one({
                "_id": e_id,
                "subject": subject,
                "body": body,
                "sentiment_score": sentiment_score,
                "sentiment_category": sentiment_category,
                "summary": summary_of_email,
                "action": bestCourseOfAction,
                "date": date,
                "time": time
            })

            if not is_new_collection:
                collection.update_one(
                    {"_id": "metadata"},
                    {"$inc": {"total_sentiment": sentiment_score}}
                )

        # --- Track sentiment trend ---
        trend_collection_name = f"{sender_mail}_trend"
        trend_collection = db[trend_collection_name]

        if not trend_collection.find_one({"_id": e_id}):
            trend_collection.insert_one({
                "_id": e_id,
                "timestamp": f"{date} {time}",
                "sentiment_score": sentiment_score
            })
        else:
            print(f"Trend already tracked for email_id {e_id}, skipping.")

        return True

    except Exception as e:
        print(f"Error occurred in email_entry: {e}")
        return False
