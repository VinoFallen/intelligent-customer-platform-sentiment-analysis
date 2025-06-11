from pymongo import MongoClient
from datetime import datetime
import re
import dotenv, os

# MongoDB URI
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)

db = client["sentiment_db"]


def email_entry(info_dict):
    try:
        # --- Extract fields ---
        e_id = info_dict['id']
        sender = info_dict['sender']
        subject = info_dict['subject']
        body = info_dict['body']
        timestamp = info_dict['timestamp']
        sentiment_score = 0.0
        sentiment_category = "None"

        # --- Extract sender name and email ---
        match = re.match(r'(.+?)\s*<(.+?)>', sender)
        if match:
            sender_name = match.group(1)
            sender_mail = match.group(2)
        else:
            sender_name = ''
            sender_mail = sender  # fallback

        # --- Convert timestamp to date and time ---
        dt = datetime.fromtimestamp(timestamp)
        date = dt.strftime("%Y-%m-%d")
        time = dt.strftime("%H:%M:%S")

        # --- Check for collection ---
        collection_name = sender_mail
        collection_names = db.list_collection_names()

        if collection_name not in collection_names:

            collection = db[collection_name]
            # Create new collection and insert two documents
            collection.insert_one({
                "sender_name": sender_name
            })
            collection.insert_one({
                "_id": e_id,
                "subject": subject,
                "body": body,
                "sentiment_score": sentiment_score,
                "sentiment_category": sentiment_category,
                "date": date,
                "time": time
            })
            print(f"Collection '{collection_name}' created and documents inserted.")
        else:
            collection = db[collection_name]
            # Collection exists, insert email entry only
            collection.insert_one({
                "_id": e_id,
                "subject": subject,
                "body": body,
                "sentiment_score": sentiment_score,
                "sentiment_category": sentiment_category,
                "date": date,
                "time": time
            })
            print(f"Entry added to existing collection '{collection_name}'.")

        return True 

    except Exception as e:
        print(f"Error occurred: {e}")
        return False  


# returns 2 values
# 1. info (dictionary) : which contains Info example ==> {'sender': 'Akshith Shetty'}
# 2. email_entries which returns list of documents. Each document is a dictionary which has details about spectfic emails
#       Example:  [
#                   {'_id': '001', 'subject': 'Test Email', 'body': 'This is a test email for unit testing.', 'date': '2025-06-11 10:33:14', 'sentiment_score': 0.85, 'sentiment_category': 'Positive'}
#                   {'_id': '002', 'subject': 'Test Email', 'body': 'This is a test email for unit testing.', 'date': '2025-06-11 10:33:51', 'sentiment_score': 0.44, 'sentiment_category': 'Negative'}
#                  ]

def get_email_entries(email):
    try:
        collection_name = email
        if collection_name not in db.list_collection_names():
            print(f"No collection named '{collection_name}' found.")
            return None

        collection = db[collection_name]
        documents = list(collection.find())

        if not documents:
            print("Collection is empty.")
            return None

        # First document contains id and sender
        info = {
            "sender": documents[0].get("sender")
        }

        # Remaining documents are email entries
        email_entries = documents[1:]  # All documents except the first

        return info, email_entries
        

    except Exception as e:
        print(f"Error retrieving email entries: {e}")
        return None


