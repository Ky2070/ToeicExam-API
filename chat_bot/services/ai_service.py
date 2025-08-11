# chat_bot/services/ai_service.py
from chat_bot.utils.ai_client import call_ai

class AIService:
    @staticmethod
    def generate_bot_reply(prompt: str) -> str:
        """
        Gọi AI với prompt tùy chỉnh.
        'prompt' có thể là bất kỳ nội dung nào người dùng hoặc hệ thống gửi.
        """
        return call_ai(prompt)
