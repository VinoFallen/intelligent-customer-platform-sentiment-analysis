#listener.py

from fastapi import FastAPI, Request
import uvicorn
import json
from gmail_reader import gmail_email_fetching
from gmail_watch_setup import setup_watch
from starlette.responses import JSONResponse

app = FastAPI()
setup_watch()
@app.post("/gmail-pubsub")
async def gmail_webhook(request: Request):
    data = await request.body()
    try:
        envolope = json.loads(data)
        if "message" in envolope:
            print(gmail_email_fetching())
            return JSONResponse(content={"status": "received"}, status_code=200)
    except Exception as e:
        print(f"Webhook Error: {e}")
        return JSONResponse(content={"error": "failed"}, status_code=500)
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)