# /backend/api_client.py

import requests
import os
from dotenv import load_dotenv
load_dotenv()

HF_API_URL = os.getenv("HF_API_URL")

def analyze_sentiment_and_summary(email_body):
    payload = {
        "email_body": email_body
    }
    if HF_API_URL is None:
        return {"error": "HF_API_URL environment variable is not set."}
    try:
        response = requests.post(HF_API_URL, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
