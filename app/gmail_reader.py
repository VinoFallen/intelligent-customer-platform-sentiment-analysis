#gamil_reader.py

import os
import re
import base64
# from dateutil import parser as dtp # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def gmail_email_authentication():
    # Authenticate and return the Gmail service.
    creds = None
    # Check if token.json exists for stored credentials, if not, create it.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/etc/secrets/credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", 'w') as token:
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
            # print(message)
            try:
                payload = message['payload']
                headers = payload['headers']
                
                subject = None
                sender = None
                timestamp = None
                for i in headers:
                    if i['name'] == 'Subject':
                        subject = i['value']
                    if i['name'] == 'From':
                        sender = i['value']
                    if i['name'] == 'Date':
                        timestamp = i['value'] 
                        
                # if timestamp is not None:
                #     dtp.parse(timestamp)        
                
                data = payload.get('parts')[0]['body']['data']
                # Gmail API returns base64url encoded data, need to decode it
                decoded_body = base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
                decoded_body = re.sub(r'\s+',' ', decoded_body).strip()
                
                service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
                
                return {'id':msg_id, 'sender':sender, 'subject':subject, 'body':decoded_body, 'timestamp':timestamp} 
            except:
                pass
        
    except HttpError as error:
        print(error)
     
     
def gmail_email_fetching(email):
    creds = gmail_email_authentication()
    if creds:
        result = get_gmail_email(creds, email)
        return result
        

if __name__ == "__main__":
    print(gmail_email_fetching('achalacharya01@gmail.com'))