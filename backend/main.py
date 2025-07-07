#/backend/main.py

from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse
import json
import asyncio
from gmail_reader import gmail_email_fetching
from gmail_watch_setup import setup_watch
from database_functions import email_entry

app = FastAPI()
processing_lock = asyncio.Lock()

MONITORED_EMAILS = [
    "achalacharya01@gmail.com",
    "nnm22am019@nmamit.in",
    "akshithk56@gmail.com"
]

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Gmail Pub/Sub listener is running."}

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/setup-gmail-watch")
async def trigger_watch_setup():
    setup_watch()
    return {"status": "watch triggered"}

@app.post("/gmail-pubsub")
async def gmail_webhook(request: Request):
    data = await request.body()
    try:
        envelope = json.loads(data)
        if "message" in envelope:
            async with processing_lock:
                for monitored_email in MONITORED_EMAILS:
                    email = gmail_email_fetching(monitored_email)
                    print(email)
                    email_entry(email)
                return JSONResponse(content={"status": "processed"}, status_code=200)
    except Exception as e:
        print(f"Webhook Error: {e}")
        return JSONResponse(content={"error": "failed"}, status_code=500)

 

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)