"""Wrapper minimal para Groq (reusado del caso 1)."""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client = None

def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def generate(prompt: str, system: str = "", model: str = "llama-3.3-70b-versatile", temperature: float = 0.3) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = get_client().chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=2000,
    )
    return resp.choices[0].message.content