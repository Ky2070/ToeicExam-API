from pathlib import Path
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load API Key từ file .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
api_key = os.getenv("GEMINI_API_KEY")
# Cấu hình API Key
genai.configure(api_key=api_key)
# Chọn mô hình Gemini
model = genai.GenerativeModel("gemini-1.5-flash")


def analyze_toeic_question(question_data):
    """
    Phân tích câu hỏi TOEIC để xác định nó thuộc phần nào (Listening hay Reading) và Part nào (1-7).

    Parameters:
        question_data (dict): JSON object chứa "question_text" và "answers".

    Returns:
        str: Kết quả phân tích từ AI.
    """
    question_text = question_data["question_text"]
    answers = question_data["answers"]
    audios = question_data["audio"]
    images = question_data["image"]
    # Định dạng danh sách đáp án từ JSON
    formatted_answers = "\n".join([f"({chr(65 + i)}) {ans}" for i, ans in enumerate(answers)])
    toeic_question = f"""
    Question:
    {question_text}
    {formatted_answers}
    {audios}
    {images}
    
    """
    prompt = f"""
    Dưới đây là một câu hỏi trong bài thi TOEIC:
    {toeic_question}
    Hãy phân tích câu hỏi này thuộc phần nào của bài thi TOEIC (Listening hay Reading) và xác định nó thuộc Part nào (Part 1, 2, 3, 4, 5, 6, hoặc 7). Giải thích lý do tại sao.
    """
    # Gửi yêu cầu phân tích đến Gemini
    response = model.generate_content(prompt)
    return response.text


# Ví dụ sử dụng với JSON object
# question_json = {
#     "question_text": "John ______ to the meeting because he was feeling sick.",
#     "answers": ["didn't go", "hasn't gone", "won't go", "doesn't go"]
# }
question_json = {
    "audio":"https://s4-media1.study4.com/media/tez_media/sound/eco_toeic_1000_test_2_1.mp3",
    "image": [],
    "question_text": "What is offered for teenage students?",
    "answers": ["A hands-on experience", " A weekly after-school class", "A complimentary souvenir", "A discounted ticket price"]
}

# Gọi hàm để phân tích
analysis_result = analyze_toeic_question(question_json)

# In kết quả phân tích
print(analysis_result)
