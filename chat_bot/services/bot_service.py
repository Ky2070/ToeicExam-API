# from django.urls import reverse
# from django.conf import settings
import random
from typing import List, Dict, Optional
from chat_bot.utils.ai_client import call_ai
from chat_bot.models import Message
from EStudyApp.services.history_service import HistoryService
from Authentication.permissions import IsTeacher
import re
from django.contrib.auth import get_user_model

User = get_user_model()
class BotService:
    """Service for generating bot responses using AI model"""

    def __init__(self):
        # Placeholder responses for demonstration
        # In a real implementation, this would integrate with an AI model
        # reverse sẽ tạo ra path '/chat_bot/history/latest'
        # self.history_latest_path = reverse("chat_bot:history_score")
        # # BASE_API_URL lấy từ settings, ví dụ 'http://localhost:8000' hoặc production URL
        # self.api_base_url = f"{settings.BASE_API_URL}{self.history_latest_path}"
        self.history_service = HistoryService()
        self.responses = [
            "I'm a helpful AI assistant. How can I help you today?",
            "That's an interesting question! Let me think about that.",
            "I understand what you're asking. Here's my response.",
            "Thank you for your message. I'm here to assist you.",
            "I appreciate you reaching out. How else can I help?",
            "That's a great point! Let me provide some insights.",
            "I'm processing your request. Here's what I think.",
            "Thanks for sharing that with me. I'm here to help!",
            "I see what you mean. Let me give you my perspective.",
            "That's something I can definitely help you with!",
        ]


    def _extract_student_identifier(self, message: str) -> Optional[str]:
        """
        Tìm ID hoặc username sinh viên từ câu hỏi.
        Ví dụ: "Kết quả sinh viên namnv" hoặc "Xem điểm student 1023"
        """
        match = re.search(r"(?:sinh viên|student)\s+([A-Za-z0-9_]+)", message, re.IGNORECASE)
        return match.group(1) if match else None

    def generate_response(self, user: User, user_message: str, conversation_history=None) -> str:
        try:
            if user and user.is_authenticated:
                print("Username:", user.username)
                print("Role:", getattr(user, "role", None))
                print("FirstName:", user.first_name)
                print("LastName:", user.last_name)
                print("Email:", user.email)
            else:
                print("Người dùng chưa đăng nhập hoặc không xác thực.")

            clean_message = user_message.strip()

            # Nếu phát hiện câu hỏi có chứa sinh viên / student
            student_identifier = self._extract_student_identifier(clean_message)
            if student_identifier:
                # Chỉ cho giáo viên hoặc admin xem dữ liệu
                if getattr(user, "role", None) not in ["teacher", "admin"]:
                    return "Bạn không có quyền xem thông tin điểm của sinh viên."

                results = self.history_service.get_latest_results(student_identifier, limit=3)
                if results:
                    history_lines = [
                        f"- {r['date']}: {r['test_name']} | Tổng: {r['score']} "
                        f"(Listening: {r['listening_score']}, Reading: {r['reading_score']})"
                        for r in results
                    ]
                    history_text = "\n".join(history_lines)
                    clean_message += (
                        f"\n\nDữ liệu kết quả thi gần nhất:\n{history_text}\n\n"
                        f"Hãy phân tích và nhận xét dựa trên kết quả trên và đưa ra lộ trình cho sinh viên cải thiện"
                    )
                else:
                    clean_message += f"\n\nKhông tìm thấy kết quả cho sinh viên '{student_identifier}'."

            return call_ai(clean_message)

        except Exception as e:
            print("AI call failed:", e)
            return "Xin lỗi, hiện tại tôi không thể phản hồi. Bạn có thể thử lại sau."


    def analyze_sentiment(self, message: str) -> str:
        """
        Analyze the sentiment of a message (placeholder)

        Args:
            message: The message to analyze

        Returns:
            Sentiment as string (positive, negative, neutral)
        """
        # Simple keyword-based sentiment analysis
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "love",
            "like",
            "happy",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "dislike",
            "sad",
            "angry",
            "frustrated",
            "problem",
        ]

        message_lower = message.lower()

        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def should_ask_followup(self, user_message: str) -> bool:
        """
        Determine if the bot should ask a follow-up question

        Args:
            user_message: The user's message

        Returns:
            Boolean indicating whether to ask follow-up
        """
        # Simple logic to determine follow-up questions
        short_responses = ["yes", "no", "ok", "sure", "maybe"]
        return user_message.lower().strip() in short_responses
