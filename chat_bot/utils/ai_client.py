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

def call_ai(prompt: str, max_words: int = 800) -> str:
    # Thêm yêu cầu giới hạn từ trong prompt
    limited_prompt = f"{prompt}\n\n(Trả lời ngắn gọn, tối đa {max_words} từ.)",
    print(limited_prompt)
    response = model.generate_content(
        limited_prompt,
        stream=False,
        generation_config=genai.types.GenerationConfig(temperature=0.5),
        safety_settings={
            "HARASSMENT": "BLOCK_NONE",
            "HATE": "BLOCK_NONE",
            "SEXUAL": "BLOCK_NONE",
            "DANGEROUS": "BLOCK_NONE"
        }
    )
    # Cắt thủ công để đảm bảo
    # text = response.text.strip()
    # words = text.split()
    # if len(words) > max_words:
    #     text = ' '.join(words[:max_words]) + '...'

    return response.text
