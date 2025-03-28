# classify_question.py
import json
import openai
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Tải biến môi trường từ file .env
load_dotenv()

# Cấu hình API key từ OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')


# Hàm tạo embedding cho câu hỏi
def create_embedding(question_text):
    try:
        response = openai.Embedding.create(
            model="text-embedding-3-small",  # Sử dụng mô hình embedding
            input=question_text
        )
        embedding = response['data'][0]['embedding']  # Lấy embedding của câu hỏi
        return embedding
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


# Hàm tính cosine similarity giữa hai vector
def calculate_cosine_similarity(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]


# Đọc embeddings từ file JSON
def load_embeddings_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)


# Đọc embeddings cho từng phần
part_1_embeddings = load_embeddings_from_file('part_1_embeddings.json')
part_2_embeddings = load_embeddings_from_file('part_2_embeddings.json')
part_3_embeddings = load_embeddings_from_file('part_3_embeddings.json')
part_4_embeddings = load_embeddings_from_file('part_4_embeddings.json')
part_5_embeddings = load_embeddings_from_file('part_5_embeddings.json')
part_6_embeddings = load_embeddings_from_file('part_6_embeddings.json')
part_7_embeddings = load_embeddings_from_file('part_7_embeddings.json')

# Danh sách các embedding theo phần
all_part_embeddings = {
    "Part 1": part_1_embeddings,
    "Part 2": part_2_embeddings,
    "Part 3": part_3_embeddings,
    "Part 4": part_4_embeddings,
    "Part 5": part_5_embeddings,
    "Part 6": part_6_embeddings,
    "Part 7": part_7_embeddings
}


# Phân loại câu hỏi mới
def classify_new_question(question_text):
    # Tạo embedding cho câu hỏi mới
    question_embedding = create_embedding(question_text)

    if not question_embedding:
        return None

    # So sánh với các phần TOEIC đã lưu trong cơ sở dữ liệu
    similarities = {}
    for part, embeddings in all_part_embeddings.items():
        part_similarity = [calculate_cosine_similarity(question_embedding, part_embedding) for part_embedding in
                           embeddings]
        max_similarity = max(part_similarity)
        similarities[part] = max_similarity

    # Tìm phần có độ tương đồng cao nhất
    most_similar_part = max(similarities, key=similarities.get)

    return most_similar_part


# Kiểm tra phân loại câu hỏi
question = "What is the deadline for the report?"  # Thay đổi câu hỏi ở đây để thử
result = classify_new_question(question)
print(f"The question belongs to: {result}")
