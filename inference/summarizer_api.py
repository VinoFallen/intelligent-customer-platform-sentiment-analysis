# /inference/summarizer_api.py

from google import generativeai as genai
import os
from dotenv import load_dotenv
import ast

load_dotenv()

my_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=my_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

def summarize_email(email_body: str, sentiment: str):
    prompt = f"""
You are a professional AI assistant supporting an employee in handling client communications. Your task is to assist the employee by analyzing the sentiment and content of incoming emails and offering helpful insights.

The client's sentiment has already been analyzed and falls under one of the following categories:
- Neutral (General)
- Neutral (Action-Oriented)
- Negative
- Positive

Given the sentiment and the email content, your responsibilities are:

1. Under the heading 'Summary:', write a concise, professional summary of the client's message. Do not mention whether any context is present or missing—focus solely on summarizing the content based on the provided email.

2. Under the heading 'Best Course of Action:', suggest what the employee should do next and keep it shorter than the summary. Your advice should aim to maintain or improve the client's sentiment, ensuring that future communication does not become negative. Be proactive and constructive, even if the email doesn't contain a direct complaint or question.

Avoid bullet points or Markdown formatting. The output should include exactly two short, well-structured paragraphs with the specified headings. The output will be a Python dictionary, with the 2 headings as the 2 keys. Don't justify why you say anything.

Sentiment: {sentiment}
Email: {email_body}
"""
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip("```python\n").strip("```").strip()
        summary_dict = ast.literal_eval(raw_text)
        summary_dict = {k.rstrip(':'): v for k, v in summary_dict.items()}
        return summary_dict
    except Exception as e:
        return {"error": str(e)}


# if __name__ == '__main__':
#     email_body = "Would you mind reviewing these onboarding documents?"
#     sentiment = "Neutral (Action-Oriented)"
#     summary = summarize_email(email_body, sentiment)
#     # print(summary)
#     print(summary['Summary'])
#     print(summary['Best Course of Action'])