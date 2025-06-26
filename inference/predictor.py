# /inference/predictor.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import os
from dotenv import load_dotenv

os.environ["TRANSFORMERS_CACHE"] = "/tmp/hf"

load_dotenv()

model = None
tokenizer = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

id2label = {
    0: "Positive",
    1: "Negative",
    2: "Neutral (General)",
    3: "Neutral (Action-Oriented)"
}

def load_model():
    global model, tokenizer
    if model is None or tokenizer is None:
        print("Loading model into memory...")
        
        
        model = AutoModelForSequenceClassification.from_pretrained(
            "ValInk/debertaXsmallFinetuned", token=os.getenv("HF_TOKEN")
        ).to(device)
        tokenizer = AutoTokenizer.from_pretrained(
            "ValInk/debertaXsmallFinetuned", token=os.getenv("HF_TOKEN")
        )
        model.eval()
        print("Model loaded and ready.")

def predict_sentiment(text: str):
    if not model or not tokenizer:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    if not text or not isinstance(text, str):
        return {"label": "Invalid", "confidence": 0.0}

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=-1).item()
        confidence = probs[0][int(pred)].item()

    return {
        "label": id2label[int(pred)],
        "confidence": round(confidence, 4)
    }



# For local testing
# if __name__ == "__main__":
#     load_model()
#     test_text = "Thank you for the update, can you send me the audit report?"
#     result = predict_sentiment(test_text)
#     print(result)
