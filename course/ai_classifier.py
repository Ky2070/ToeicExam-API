# import openai
# from dotenv import load_dotenv
# import os
# # Tải biến môi trường từ file .env
# load_dotenv()
# # Cấu hình API key từ OpenAI bằng cách lấy từ biến môi trường
# openai.api_key = os.getenv('OPENAI_API_KEY')
# # Hàm phân tích câu hỏi TOEIC
# def classify_toeic_question(question_text):
#     try:
#         # Gọi GPT-4 để phân tích câu hỏi
#         response = openai.ChatCompletion.create(
#             model="gpt-4",  # Sử dụng mô hình GPT-4
#             messages=[
#                 {
#                     "role": "user",
#                     "content": f"Given the TOEIC question: '{question_text}', determine which part of the TOEIC exam it belongs to. The options are: Part 1, Part 2, Part 3, Part 4, Part 5, Part 6, Part 7. Return only the part number."
#                 }
#             ]
#         )
#         # Trả về phần câu hỏi
#         return response['choices'][0]['message']['content'].strip()
#
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return None

import openai
from dotenv import load_dotenv
import os

# Tải biến môi trường từ file .env
load_dotenv()

# Cấu hình API key từ OpenAI bằng cách lấy từ biến môi trường
openai.api_key = os.getenv('OPENAI_API_KEY')


# Hàm phân tích câu hỏi TOEIC
def classify_toeic_question(question_text):
    try:
        # Gọi GPT-4 để phân tích câu hỏi
        response = openai.completions.create(
            model="gpt-3.5-turbo",  # Sử dụng mô hình GPT-4
            prompt=f"Given the TOEIC question: '{question_text}', determine which part of the TOEIC exam it belongs to. The options are: Part 1, Part 2, Part 3, Part 4, Part 5, Part 6, Part 7. Return only the part number.",
            max_tokens=10  # Giới hạn độ dài của câu trả lời
        )

        # Trả về phần câu hỏi
        return response['choices'][0]['text'].strip()

    except Exception as e:
        print(f"Error occurred: {e}")
        return None
