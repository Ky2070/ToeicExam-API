# chat_bot/utils/ai_client.py
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def call_ai(prompt: str) -> str:
    response = model.generate_content(
        prompt,
        stream=False,
        generation_config=genai.types.GenerationConfig(temperature=0.5),
        safety_settings={
            "HARASSMENT": "BLOCK_NONE",
            "HATE": "BLOCK_NONE",
            "SEXUAL": "BLOCK_NONE",
            "DANGEROUS": "BLOCK_NONE"
        }
    )
    return response.text
