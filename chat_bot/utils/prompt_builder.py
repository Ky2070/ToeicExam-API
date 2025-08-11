# chat_bot/utils/prompt_builder.py
class PromptBuilder:
    @staticmethod
    def build_prompt(user_message: str) -> str:
        msg_lower = user_message.lower()

        if "toeic" in msg_lower or "listening" in msg_lower or "reading" in msg_lower:
            return f"""
            Bạn là trợ lý luyện thi TOEIC. Người dùng hỏi: "{user_message}".
            Hãy trả lời chính xác, ngắn gọn, dễ hiểu.
            """
        elif "dịch" in msg_lower or "translate" in msg_lower:
            return f"""
            Dịch đoạn văn sau sang tiếng Việt, giữ nguyên nghĩa và phong cách:
            "{user_message}"
            """
        elif "ảnh" in msg_lower or "image" in msg_lower:
            return f"""
            Mô tả nội dung bức ảnh mà người dùng vừa gửi: "{user_message}"
            """
        else:
            # Chat thông thường
            return f"Người dùng nói: '{user_message}'. Trả lời tự nhiên, thân thiện."
