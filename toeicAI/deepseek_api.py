import requests
import json

# Cấu hình API Key
API_KEY = "your_deepseek_api_key"  # Thay bằng API Key của bạn
API_URL = "https://api.deepseek.com/v1/chat/completions"


def classify_toeic_question(question_text):
    """
    Gửi câu hỏi TOEIC đến DeepSeek để phân loại nó vào Part 1-7.
    """

    # Nếu không có câu hỏi, trả về lỗi
    if not question_text:
        return "Không xác định"

    # Header để gọi API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Prompt hướng dẫn AI phân loại câu hỏi
    prompt = f"""
    Bạn là chuyên gia về kỳ thi TOEIC. Hãy phân loại câu hỏi sau vào đúng phần (Part 1-7).

    Câu hỏi: "{question_text}"

    - Nếu câu hỏi liên quan đến mô tả hình ảnh, hãy trả về: "Part 1"
    - Nếu câu hỏi là một hội thoại ngắn (câu đơn), hãy trả về: "Part 2"
    - Nếu câu hỏi có hội thoại dài giữa hai người, hãy trả về: "Part 3"
    - Nếu câu hỏi là thông báo hoặc bài nói, hãy trả về: "Part 4"
    - Nếu câu hỏi yêu cầu chọn từ phù hợp vào chỗ trống, hãy trả về: "Part 5"
    - Nếu câu hỏi là đoạn văn ngắn với nhiều câu trống, hãy trả về: "Part 6"
    - Nếu câu hỏi là một bài đọc dài, hãy trả về: "Part 7"

    Hãy chỉ trả về kết quả dưới định dạng JSON như sau:
    {{"part": "Part X"}}
    """

    # Dữ liệu gửi đến API
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    # Gửi request đến API
    response = requests.post(API_URL, json=payload, headers=headers)

    # Kiểm tra xem request có thành công không
    if response.status_code == 200:
        result = response.json()
        try:
            # Trích xuất nội dung từ kết quả trả về
            part_prediction = json.loads(result["choices"][0]["message"]["content"])
            return part_prediction.get("part", "Không xác định")
        except json.JSONDecodeError:
            return "Không xác định"
    else:
        return f"Lỗi API: {response.status_code}"
