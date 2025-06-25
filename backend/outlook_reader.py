# import requests
# from microsoft_auth import get_access_token_from_file  # Make sure this import path is correct

# GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# def get_unread_emails_from_client(client_email: str):
#     access_token = get_access_token_from_file()
#     if not access_token:
#         print("[ERROR] Access token is missing or invalid.")
#         return

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Accept": "application/json"
#     }

#     # Fetch unread messages from inbox
#     url = f"{GRAPH_API_BASE}/me/messages?$filter=isRead eq false&$top=50"

#     response = requests.get(url, headers=headers)
#     if response.status_code != 200:
#         print(f"[ERROR] Failed to fetch unread emails: {response.status_code} - {response.text}")
#         return

#     messages = response.json().get("value", [])
#     if not messages:
#         print(" No unread emails found.")
#         return

#     # Filter messages by client email
#     client_emails = [
#         msg for msg in messages
#         if msg.get("from", {}).get("emailAddress", {}).get("address", "").lower() == client_email.lower()
#     ]

#     if not client_emails:
#         print(f"No unread emails from client: {client_email}")
#         return

#     print(f"Found {len(client_emails)} unread email(s) from {client_email}:\n")
#     for idx, msg in enumerate(client_emails, 1):
#         subject = msg.get("subject", "(No Subject)")
#         received = msg.get("receivedDateTime", "Unknown Time")

#         print(f"{idx}. Subject: {subject}")
#         print(f"   Received: {received}\n")


# if __name__ == "__main__":
#     get_unread_emails_from_client("outlook_7F75849DA29A8754@outlook.com")
