#database_functions.py

from pymongo import MongoClient
from datetime import datetime
from dateutil import parser as date_parser
import re
import dotenv, os
from .predictor import predict_sentiment
from .summarizer_api import summarize_email

# MongoDB URI
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
        if timestamp is not None:
            dt = date_parser.parse(timestamp)
            date = dt.strftime("%Y-%m-%d")
            time = dt.strftime("%H:%M:%S")
        else:
            date = ""
            time = ""


        #Predition of Sentiment
        sentiment_category, sentiment_score = call_prediction(str(body))


        #Summary and best course of action
        summary_dict = summarize_email(str(body), sentiment_category)
        summary_of_email = summary_dict['Summary']
        bestCourseOfAction = summary_dict['Best Course of Action']
        
        # --- Check for collection ---
        collection_name = sender_mail
        collection_names = db.list_collection_names()
        collection = db[collection_name]

        # Flag to indicate if new collection
        is_new_collection = collection_name not in collection_names

        # --- Insert initial sender doc if new collection ---
        if is_new_collection:
            collection.insert_one({
                "_id": "metadata",
                "sender_name": sender_name,
                "total_sentiment": sentiment_score
            })

        # --- Check for duplicate email entry ---
        if collection.find_one({"_id": e_id}):
            print(f"Duplicate entry with _id {e_id} already exists. Skipping insertion.")
        else:
            # Insert the email
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

            # Only increment if not a new collection
            if not is_new_collection:
                collection.update_one(
                    {"_id": "metadata"},
                    {"$inc": {"total_sentiment": sentiment_score}}
                )


        # Read updated total sentiment
        metadata_doc = collection.find_one({"_id": "metadata"})
        if metadata_doc is not None:
            new_total_sentiment = metadata_doc.get("total_sentiment", 0.0)
        else:
            new_total_sentiment = 0.0

        # Insert snapshot into separate trend collection
        trend_collection_name = f"{sender_mail}_trend"
        trend_collection = db[trend_collection_name]

        trend_collection.insert_one({
            "timestamp": f"{date} {time}",
            "total_sentiment": new_total_sentiment
        })



        return True 

    except Exception as e:
        print(f"Error occurred: {e}")
        return False  



def call_prediction(body: str):
    pred = predict_sentiment(str(body))
    sentiment_category = pred['label']
    sentiment_score = 0.0  
    if sentiment_category == 'Positive':
        sentiment_score = 2
    elif sentiment_category == 'Negative':
        sentiment_score = -3
    elif sentiment_category == 'Neutral (General)':
        sentiment_score = 1
    elif sentiment_category == 'Neutral (Action-Oriented)':
        sentiment_score = 0.5

    return sentiment_category, sentiment_score
