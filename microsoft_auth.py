from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
import requests
import os
import json
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Load env variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
redirect_uri = os.getenv("REDIRECT_URI")
scopes = os.getenv("SCOPES")

auth_base = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0"
token_file = os.path.join(os.path.dirname(__file__), "token_microsoft.json")

@app.get("/")
async def login():
    query_params = urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "response_mode": "query",
        "scope": scopes
    })
    auth_url = f"{auth_base}/authorize?{query_params}"
    print(f"[DEBUG] Login URL: {auth_url}")
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No code in callback"}, status_code=400)

    token_url = f"{auth_base}/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": scopes
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()

    if "access_token" not in token_data:
        print(f"[ERROR] Token response: {token_data}")
        return JSONResponse({"error": "Failed to get access token", "details": token_data}, status_code=400)

    try:
        print(f"[DEBUG] Saving token to: {token_file}")
        with open(token_file, "w") as f:
            json.dump(token_data, f)
    except Exception as e:
        print(f"[ERROR] Failed to save token: {e}")
        return JSONResponse({"error": f"Failed to save token: {e}"}, status_code=500)

    return HTMLResponse("<h1>Authentication successful! You can close this window.</h1>")

def get_access_token_from_file():
    try:
        with open(token_file, "r") as f:
            token_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Reading token file: {e}")
        return None

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if access_token:
        return access_token

    if not refresh_token:
        print("[ERROR] No refresh token found. Please re-authenticate.")
        return None

    print("[INFO] Access token missing or expired. Attempting to refresh.")
    token_url = f"{auth_base}/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "redirect_uri": redirect_uri,
        "scope": scopes
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        print(f"[ERROR] Failed to refresh token: {response.text}")
        return None

    new_token_data = response.json()
    try:
        with open(token_file, "w") as f:
            json.dump(new_token_data, f)
        print("[INFO] Token refreshed and saved.")
    except Exception as e:
        print(f"[ERROR] Failed to save refreshed token: {e}")
        return None

    return new_token_data.get("access_token")
