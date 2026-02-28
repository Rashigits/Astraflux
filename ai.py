import requests
from config import GROQ_API_KEY

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ai_chat(message: str) -> str:
    r = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        },
        timeout=30
    )

    if r.status_code != 200:
        return f"Groq error: {r.text}"

    return r.json()["choices"][0]["message"]["content"]
