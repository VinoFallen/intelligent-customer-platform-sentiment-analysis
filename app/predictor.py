# /app/predictor.py

from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Dynamically resolve the model path
MODEL_PATH = Path(__file__).parent / "debertaFinetunedFinal"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()


id2label = {
    0: "Positive",
    1: "Negative",
    2: "Neutral (General)",
    3: "Neutral (Action-Oriented)",
}

def predict_sentiment(text: str):
    if not text or not isinstance(text, str):
        return {"label": "Invalid", "confidence": 0.0}

    # Tokenize and send to device
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=-1).item()
        confidence = probs[0][int(pred)].item()

    return {
        "label": id2label[int(pred)],
        "confidence": round(confidence, 4)
    }


if __name__ == "__main__":
    email_example_text = "Thank you for the update, can you send me the audit report?"  
    prediction = predict_sentiment(email_example_text)
    
    print(prediction)
    print("Label:", prediction["label"])
    print("Confidence:", prediction["confidence"])
