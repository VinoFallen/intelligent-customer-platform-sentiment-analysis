#/backend/gmail_reader.py

import os
import re
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def gmail_email_authentication():
    creds = None

    is_render = os.getenv("RENDER", "").lower() == "true"  # safer
    if is_render:
        token_path = "/tmp/token.json"
        creds_path = "/etc/secrets/credentials.json"
        initial_token_secret_path = "/etc/secrets/token.json"

        print(f"Render detected. Using token path: {token_path}")
        print(f"Checking if token exists at {token_path}: {os.path.exists(token_path)}")
        print(f"Checking if secret token exists at {initial_token_secret_path}: {os.path.exists(initial_token_secret_path)}")

        # Copy token from secret if not already in /tmp
        if not os.path.exists(token_path) and os.path.exists(initial_token_secret_path):
            print("Copying token.json from secrets to /tmp...")
            with open(initial_token_secret_path, 'r') as src, open(token_path, 'w') as dst:
                dst.write(src.read())
    else:
        token_path = "token.json"
        creds_path = "credentials.json"

    # Load token file
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Refresh or run auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                raise Exception("Token refresh failed. Re-authenticate locally and upload a new token.json as secret.")
        else:
            if is_render:
                raise Exception("No valid token. Re-authenticate locally and upload token.json as a secret.")
            # Local auth flow
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

    return creds




def get_gmail_email(creds, receive_email_id):
    try:
        service = build('gmail', 'v1', credentials=creds)
        query = f"is:unread from:{receive_email_id}"

        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No unread messages found from sender.")
            return

        for msg in messages:
            msg_id = msg['id']
            message = service.users().messages().get(userId='me', id=msg_id).execute()
            try:
                payload = message['payload']
                headers = payload['headers']
                
                subject = None
                sender = None
                timestamp = None
                for h in headers:
                    if h['name'] == 'Subject':
                        subject = h['value']
                    elif h['name'] == 'From':
                        sender = h['value']
                    elif h['name'] == 'Date':
                        timestamp = h['value'] 
                
                parts = payload.get('parts')
                if parts:
                    data = parts[0]['body']['data']
                else:
                    data = payload['body'].get('data', '')

                decoded_body = base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
                decoded_body = re.sub(r'\s+', ' ', decoded_body).strip()

                # Mark message as read
                service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

                return {
                    'id': msg_id,
                    'sender': sender,
                    'subject': subject,
                    'body': decoded_body,
                    'timestamp': timestamp
                }
            except Exception as e:
                print(f"Error parsing message: {e}")
                continue

    except HttpError as error:
        print(f"Gmail API error: {error}")


def gmail_email_fetching(email):
    creds = gmail_email_authentication()
    if creds:
        return get_gmail_email(creds, email)


# if __name__ == "__main__":
#     print(gmail_email_fetching('achalacharya01@gmail.com'))
