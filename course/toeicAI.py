from pathlib import Path
import google.generativeai as genai
import os
import json
from PIL import Image
import requests
from io import BytesIO
from pydub import AudioSegment
import speech_recognition as sr
import pytesseract
from dotenv import load_dotenv
import django

# Thiết lập biến môi trường trước khi import models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EnglishApp.settings')  # Thay bằng tên project thực của bạn
django.setup()

from EStudyApp.models import History

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ Thêm ffmpeg vào PATH để subprocess tìm thấy
os.environ["PATH"] += os.pathsep + r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin"

# 🔧 Đặt lại converter và ffprobe cho Pydub
AudioSegment.converter = r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin\ffprobe.exe"

print("✅ Kiểm tra FFmpeg:", os.path.isfile(AudioSegment.converter))
print("✅ Kiểm tra FFprobe:", os.path.isfile(AudioSegment.ffprobe))
# Load API Key từ file .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
api_key = os.getenv("GEMINI_API_KEY")
# Cấu hình API Key
genai.configure(api_key=api_key)
# Chọn mô hình Gemini
model = genai.GenerativeModel("gemini-1.5-flash")


def get_latest_user_histories(user_id, limit=3):
    latest_histories = (
        History.objects
        .filter(user_id=user_id, complete=True)
        .select_related('test')
        .order_by('-id')[:limit]  # Giả sử có trường completion_time
    )
    return latest_histories


def get_user_info_prompt_single(history, all_histories):
    """
    Tạo prompt chứa thông tin của một bài thi riêng biệt.
    Phân tích từng phần của bài thi và trả về phản hồi từ AI.
    """
    # Lọc ra các bài có cùng tên đề thi
    same_test_histories = [h for h in all_histories if h.test.name == history.test.name]

    # Sắp xếp theo thời gian hoàn thành (hoặc id nếu muốn)
    same_test_histories.sort(key=lambda h: h.completion_time)

    # Tìm chỉ số lần làm bài (tăng từ 1)
    attempt_number = same_test_histories.index(history) + 1

    user_info = f"""
Tên đề thi: {history.test.name} (Lần làm thứ {attempt_number})
Listening: {history.listening_score}
Reading: {history.reading_score}
Tổng điểm: {history.score}
Đáp án đúng: {history.correct_answers}
Tỷ lệ đúng: {history.percentage_score}%
Thời gian hoàn thành: {history.completion_time} giây
Sai: {history.wrong_answers} | Bỏ qua: {history.unanswer_questions}
"""

    prompt = f"""
Dưới đây là thông tin bài thi TOEIC của người dùng:
{user_info}
Hãy phân tích kết quả điểm số Listening và Reading trong bài thi này và đưa ra lời khuyên ngắn gọn, rõ ràng:
- Phần nào cần cải thiện, Listening hay Reading?
"""

    print(f"[DEBUG] Prompt gửi đi cho đề '{history.test.name}' - Lần {attempt_number}")
    response = model.generate_content(prompt)  # Gọi AI để phân tích
    return response.text


def get_user_info_prompt_multi(user_id):
    """
    Tạo prompt cho tất cả các bài thi của người dùng.
    Phân tích và nhận phản hồi cho từng bài thi riêng biệt.
    """
    histories = get_latest_user_histories(user_id, limit=3)  # Lấy tất cả lịch sử thi của người dùng
    if not histories:
        return "Không tìm thấy lịch sử làm bài cho người dùng này."

    # Phân tích từng bài thi và lấy phản hồi cho mỗi bài
    feedbacks = []
    for history in histories:
        feedback = get_user_info_prompt_single(history, histories)
        feedbacks.append({
            "test_name": history.test.name,
            "feedback": feedback
        })

    return feedbacks


def create_toeic_question_prompt(question_text, answers, audio=None, image=None):
    """
    Tạo prompt phân tích câu hỏi TOEIC và đưa ra đáp án đúng.

    Parameters:
        question_text (str): Nội dung câu hỏi.
        answers (dict): Dictionary chứa các đáp án.
        audio (list, optional): Danh sách URL file âm thanh (nếu có).
        image (list, optional): Danh sách URL hình ảnh (nếu có).

    Returns:
        str: Phân tích từ AI về câu hỏi TOEIC và đáp án đúng.
    """
    if not answers or not isinstance(answers, dict):
        raise ValueError("answers phải là một dictionary chứa đáp án theo dạng key-value.")

    formatted_answers = "\n".join([f"({key}) {value}" for key, value in answers.items()])
    audio_text = "\n".join(audio) if isinstance(audio, list) and audio else "Không có"
    if isinstance(image, list):
        image_text = "\n".join(image)
    elif isinstance(image, str):
        image_text = image
    else:
        image_text = "Không có"

    # Gắn tiêu đề rõ ràng để AI hiểu nội dung từ ảnh
    image_text = f"Nội dung trích xuất từ hình ảnh:\n{image_text}"

    toeic_question = f"""
    Câu hỏi:
    {question_text}
    {formatted_answers}

    Transcript: {audio_text}
    Mô tả: {image_text}
    """

    prompt = f"""
    Bạn là một chuyên gia TOEIC. Dưới đây là một câu hỏi trong bài thi TOEIC:
    {toeic_question}

    Hãy thực hiện các bước sau:

    1. Phân tích xem câu hỏi này thuộc **kỹ năng nào** (Listening hay Reading).
    2. Xác định chính xác câu hỏi này thuộc **Part mấy** trong đề thi TOEIC (Part 1 đến Part 7).
    3. **Chọn đáp án đúng nhất** trong các đáp án A, B, C, D.
    4. **Giải thích chi tiết lý do chọn đáp án đó** và tại sao các đáp án còn lại không phù hợp.

    Trả lời rõ ràng, ngắn gọn nhưng súc tích và dễ hiểu.
    """
    print("🧠 Prompt gửi đến AI:")
    print(prompt)
    response = model.generate_content(prompt)
    return response.text


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
    if isinstance(image, list):
        image_text = "\n".join(image)
    elif isinstance(image, str):
        image_text = image
    else:
        image_text = "Không có"

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
# Dữ liệu đầu vào
question_text = "What are the speakers discussing?"
answers = {
    "A": "A business trip.",
    "B": "A budget proposal.",
    "C": "An upcoming conference.",
    "D": "A package delivery."
}
audio = "https://s4-media1.study4.com/media/tez_media/sound/eco_toeic_1000_test_2_32_34.mp3"
image = None
# "https://s4-media1.study4.com/media/gg_imgs/test/9a18decce4319016bc774c19922917c0c4ff4413.jpg"
# Fetch the image from the URL
# response = requests.get(image)
# img = Image.open(BytesIO(response.content))
# # Extract text from the image
# text_img = pytesseract.image_to_string(img)
# print("Extracted Text:")
# print(text_img)
# response = requests.get(audio)
# with open("audio.mp3", "wb") as f:
#     f.write(response.content)
#
# # Chuyển mp3 sang wav
# audio = AudioSegment.from_mp3("audio.mp3")
# audio.export("audio.wav", format="wav")
#
# # Nhận dạng giọng nói
# r = sr.Recognizer()
# with sr.AudioFile("audio.wav") as source:
#     audio_data = r.record(source)
#     try:
#         transcript = r.recognize_google(audio_data)
#         print("🎧 Nội dung trích xuất từ audio:")
#         print(transcript)
#     except sr.UnknownValueError:
#         print("⚠️ Không nhận diện được nội dung.")
#     except sr.RequestError as e:
#         print(f"❌ Lỗi kết nối đến Google API: {e}")
# Gọi hàm để phân tích
analysis_result = create_toeic_question_prompt(question_text, answers, audio, image)

# In kết quả phân tích
print(analysis_result)