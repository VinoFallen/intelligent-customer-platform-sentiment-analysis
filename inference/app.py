# /inference/app.py

from fastapi import FastAPI, Request
from predictor import predict_sentiment, load_model
from summarizer_api import summarize_email
import uvicorn

app = FastAPI()

@app.on_event("startup")
def load_on_startup():
    load_model()  
    print("Model Loaded.")


@app.post("/")
async def handle_inference(request: Request):
    data = await request.json()
    body = data.get("email_body", "")

    sentiment_result = predict_sentiment(body)
    summary_result = summarize_email(body, sentiment_result["label"])

    return {
        **sentiment_result,
        **summary_result
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860)
