# save_embeddings.py
import json
import openai
from dotenv import load_dotenv
import os

# Tải biến môi trường từ file .env
load_dotenv()

# Cấu hình API key từ OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Danh sách các câu hỏi mẫu cho từng phần TOEIC
questions_part_1 = [
    "What is the man doing in the picture?",
    "Which of the following is a characteristic of the car in the image?",
    "What color is the shirt worn by the person in the image?",
    "What is the person in the picture looking at?"
]

questions_part_2 = [
    "Where is the nearest coffee shop?",
    "What time does the meeting start?",
    "How do I get to the bus station?",
    "When is the deadline for the report?"
]

questions_part_3 = [
    "Where is the conversation taking place?",
    "What is the man offering the woman?",
    "How long does the man say the event will last?",
    "What did the woman say she would do next?"
]

questions_part_4 = [
    "What is the main purpose of the speaker's presentation?",
    "How did the speaker recommend contacting customer support?",
    "What did the speaker say about the company's new product?",
    "Who is the target audience for the new service?"
]

questions_part_5 = [
    "She _____ to the store yesterday.",
    "The meeting will start _____ 10 a.m.",
    "He has been working here _____ 5 years."
]

questions_part_6 = [
    "The report was _____ on Monday.",
    "The manager is responsible _____ the final decision.",
    "The product is _____ in the new catalog."
]

questions_part_7 = [
    "What is the purpose of the letter?",
    "How many products does the company offer in its new catalog?",
    "Where is the conference being held this year?",
    "What does the advertisement promote?"
]

# Hàm tạo embedding cho câu hỏi
def create_embedding(question_text):
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",  # Sử dụng mô hình embedding
            input=question_text
        )
        embedding = response['data'][0]['embedding']  # Lấy embedding của câu hỏi
        return embedding
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Tạo embedding cho các câu hỏi mẫu
def create_embeddings_for_parts(questions):
    part_embeddings = []
    for question in questions:
        embedding = create_embedding(question)
        if embedding:
            part_embeddings.append(embedding)
    return part_embeddings

# Lưu các embeddings vào file JSON
def save_embeddings_to_file(filename, part_embeddings):
    with open(filename, 'w') as file:
        json.dump(part_embeddings, file)

# Tạo embedding cho từng phần TOEIC và lưu vào các file JSON
save_embeddings_to_file('part_1_embeddings.json', create_embeddings_for_parts(questions_part_1))
save_embeddings_to_file('part_2_embeddings.json', create_embeddings_for_parts(questions_part_2))
save_embeddings_to_file('part_3_embeddings.json', create_embeddings_for_parts(questions_part_3))
save_embeddings_to_file('part_4_embeddings.json', create_embeddings_for_parts(questions_part_4))
save_embeddings_to_file('part_5_embeddings.json', create_embeddings_for_parts(questions_part_5))
save_embeddings_to_file('part_6_embeddings.json', create_embeddings_for_parts(questions_part_6))
save_embeddings_to_file('part_7_embeddings.json', create_embeddings_for_parts(questions_part_7))

print("Embeddings đã được lưu vào các file JSON.")
