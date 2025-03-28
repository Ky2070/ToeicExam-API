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


def analyze_toeic_question(question_text, answers, audio=None, image=None):
    """
    Phân tích câu hỏi TOEIC để xác định nó thuộc phần nào (Listening hay Reading) và Part nào (1-7).

    Parameters:
        question_text (str): Nội dung câu hỏi.
        answers (dict): Dictionary chứa các đáp án theo dạng key-value, ví dụ: {"A": "Đáp án A", "B": "Đáp án B", ...}.
        audio (list, optional): Danh sách URL file âm thanh (nếu có).
        image (list, optional): Danh sách URL hình ảnh (nếu có).

    Returns:
        str: Kết quả phân tích từ AI.
    """
    # Kiểm tra answers phải là dictionary
    if not answers or not isinstance(answers, dict):
        raise ValueError("answers phải là một dictionary chứa đáp án theo dạng key-value.")

    # Định dạng danh sách đáp án từ dictionary
    formatted_answers = "\n".join([f"({key}) {value}" for key, value in answers.items()])

    # Xử lý danh sách audio và image, tránh lỗi khi không có dữ liệu
    audio_text = "\n".join(audio) if isinstance(audio, list) and audio else "None"
    image_text = "\n".join(image) if isinstance(image, list) and image else "None"

    # Tạo nội dung câu hỏi đầy đủ (không có thời gian phân tích)
    toeic_question = f"""
    Question:
    {question_text}
    {formatted_answers}

    Audio: {audio_text}
    Image: {image_text}
    """

    # Tạo prompt cho AI
    prompt = f"""
    Dưới đây là một câu hỏi trong bài thi TOEIC:
    {toeic_question}
    Hãy phân tích câu hỏi này thuộc phần nào của bài thi TOEIC (Listening hay Reading),  
    và xác định nó thuộc Part nào (Part 1, 2, 3, 4, 5, 6 hoặc 7). Giải thích lý do tại sao.
    """

    # Giả sử rằng 'model' là đối tượng AI model đã được định nghĩa toàn cục
    response = model.generate_content(prompt)
    return response.text


# Ví dụ sử dụng với JSON object
# question_json = {
#     "question_text": "John ______ to the meeting because he was feeling sick.",
#     "answers": ["didn't go", "hasn't gone", "won't go", "doesn't go"]
# }
# Dữ liệu đầu vào
question_text = "What does the speaker imply about the meeting?"
answers = {
    "A": "It has been postponed.",
    "B": "It will be held in a new location.",
    "C": "It will start earlier than planned.",
    "D": "It has been canceled."
}
audio = ["https://example.com/audio.mp3"]
image = None

# Gọi hàm để phân tích
analysis_result = analyze_toeic_question(question_text, answers, audio, image)

# In kết quả phân tích
print(analysis_result)
