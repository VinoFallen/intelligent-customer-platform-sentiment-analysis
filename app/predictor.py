# predictor.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

MODEL_PATH = "./deberta-finetuned"  

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

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

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)

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
    email_example_text = '''Hey team,  We’d appreciate an update on the status of Integrated composite paradigm.''' #Neutral (Action-Oriented)
    prediction = predict_sentiment(email_example_text)
    
    print(prediction['label'])
    print(prediction['confidence'])