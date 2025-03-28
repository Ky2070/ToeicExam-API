from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
from dotenv import load_dotenv

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


# Ví dụ: So sánh embedding của câu hỏi mới với các câu hỏi trong cơ sở dữ liệu
def classify_question_to_part(question_text, part_embeddings):
    # Tạo embedding cho câu hỏi mới
    question_embedding = create_embedding(question_text)

    if not question_embedding:
        return None

    # So sánh với các phần TOEIC đã lưu trong cơ sở dữ liệu
    similarities = [calculate_cosine_similarity(question_embedding, part_embedding) for part_embedding in
                    part_embeddings]

    # Tìm phần có độ tương đồng cao nhất
    max_similarity = max(similarities)
    part_index = similarities.index(max_similarity)

    # Giả sử bạn có một danh sách các phần TOEIC
    parts = ["Part 1", "Part 2", "Part 3", "Part 4", "Part 5", "Part 6", "Part 7"]

    return parts[part_index]
