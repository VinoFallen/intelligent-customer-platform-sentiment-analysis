#main.py

from fastapi import FastAPI, Request, Response
import uvicorn
import json
from .gmail_reader import gmail_email_fetching
from .gmail_watch_setup import setup_watch
from starlette.responses import JSONResponse
from .database_functions import email_entry

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Gmail Pub/Sub listener is running."}


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)  # No Content



@app.get("/setup-gmail-watch")
async def trigger_watch_setup():
    setup_watch()
    return {"status": "watch triggered"}


@app.post("/gmail-pubsub")
async def gmail_webhook(request: Request):
    data = await request.body()
    try:
        envolope = json.loads(data)
        if "message" in envolope:
            email = gmail_email_fetching("achalacharya01@gmail.com")
            email_entry(email)
            return JSONResponse(content={"status": "received"}, status_code=200)
    except Exception as e:
        print(f"Webhook Error: {e}")
        return JSONResponse(content={"error": "failed"}, status_code=500)
    
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)