#gmail_watch_setup.py


import subprocess
import time
import os
import requests
from googleapiclient.discovery import build
from gmail_reader import gmail_email_authentication
from google.cloud import pubsub_v1

TOPIC_NAME = "projects/gmail-client-462105/topics/gmail_notify_topic"
SUBSCRIPTION_NAME = "projects/gmail-client-462105/subscriptions/gmail_notify_topic-sub"

def update_subscription_push_endpoint(push_endpoint):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = SUBSCRIPTION_NAME

    push_config = pubsub_v1.types.PushConfig(push_endpoint=push_endpoint) # type: ignore

    with subscriber:
        subscriber.modify_push_config(
            request={
                "subscription": subscription_path,
                "push_config": push_config,
            }
        )

def start_ngrok():
    # Start ngrok on port 8000
    subprocess.Popen(["ngrok", "http", "8000"])
    time.sleep(5)  # Allow ngrok time to spin up

def get_ngrok_url():
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["public_url"].startswith("https://"):
                return tunnel["public_url"]
    except Exception as e:
        print("Error getting Ngrok URL:", e)
    return None

def setup_watch():
    start_ngrok()
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("Ngrok URL not found. Is ngrok running?")
        return

    push_endpoint = f"{ngrok_url}/gmail-pubsub"
    update_subscription_push_endpoint(push_endpoint)
    
    creds = gmail_email_authentication()
    service = build("gmail", 'v1', credentials=creds)
    
    request_body = {
        "labelIds": ["INBOX", "UNREAD"],
        "topicName": TOPIC_NAME,
    }

    response = service.users().watch(userId='me', body=request_body).execute()
    print("Watch response:", response)
    
    time.sleep(5)
    os.system('cls')
    

if __name__ == "__main__":
    setup_watch()
