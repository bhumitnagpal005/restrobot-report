import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

def _get_client():
    api_key = os.getenv("gemini_token") or os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()

_SYSTEM_PROMPT = (
    "You are a helpful assistant knowledgeable about restaurants in Vellore, India. "
    "Answer queries about menus, prices, dietary options, and restaurant details using the provided context. "
    "Be clear, concise, and directly address the question. "
    "Apply proper capitalisation and grammar without altering the information itself. "
    "If you cannot answer from the context or history, say \"I don't know\" or \"I'm not sure\". "
    "Do not add unnecessary line breaks within your response."
)


def generate_response(context: str, query: str, history_string: str) -> str:
    prompt = f"""{_SYSTEM_PROMPT}

Context:
{context}

Conversation History:
{history_string}

Question: {query}
Answer:"""

    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
    ]
    max_retries = 2

    try:
        client = _get_client()
    except Exception as e:
        print(f"[Warning] Failed to initialize Gemini client: {e}")
        client = None

    if client:
        for model_name in candidate_models:
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=model_name, 
                        contents=prompt
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    print(f"[Warning] Call to {model_name} failed (Attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(1)

    # Fallback response if all API attempts fail
    return "I'm sorry, I am currently experiencing high server traffic. Please try again in a moment."