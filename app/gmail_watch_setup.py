#gmail_watch_setup.py


import subprocess
import time
import os
import requests
from googleapiclient.discovery import build
from .gmail_reader import gmail_email_authentication
from google.cloud import pubsub_v1

TOPIC_NAME = "projects/gmail-client-462105/topics/gmail_notify_topic"
SUBSCRIPTION_NAME = "projects/gmail-client-462105/subscriptions/gmail_notify_topic-sub"

RENDER_URL = "https://intelligent-customer-platform-sentiment.onrender.com"


def setup_watch():

    creds = gmail_email_authentication()
    service = build("gmail", 'v1', credentials=creds)
    
    request_body = {
        "labelIds": ["INBOX", "UNREAD"],
        "topicName": TOPIC_NAME,
    }

    response = service.users().watch(userId='me', body=request_body).execute()
    print("Watch response:", response)
    

if __name__ == "__main__":
    setup_watch()
