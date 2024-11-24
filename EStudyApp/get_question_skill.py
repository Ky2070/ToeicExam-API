from django.http import JsonResponse

from EStudyApp.models import Question


def get_question_skill(question_id):
    # Retrieve the question object using the provided id
    question = Question.objects.get(id=question_id)  # Giả sử bạn đang sử dụng ORM như Django để truy vấn

    # Retrieve the associated part for the question
    part = question.part

    # Get the related PartDescription object
    part_description = part.part_description
    return part_description.skill


# def check_answers(user_answers):
#     listening_count = 0  # Số câu nghe
#     correct_answers_count = 0  # Số câu trả lời đúng
#
#     for answer in user_answers:
#         question_id = answer['id']
#         user_answer = answer['userAnswer']
#
#         # Lấy câu hỏi từ cơ sở dữ liệu
#         question = Question.objects.get(id=question_id)
#
#         # Lấy đáp án đúng của câu hỏi
#         correct_answer = question.correct_answer  # Giả sử trường này chứa đáp án đúng của câu hỏi
#
#         # Kiểm tra nếu câu trả lời của người dùng là đúng
#         if user_answer == correct_answer:
#             correct_answers_count += 1
#
#         # Kiểm tra loại câu hỏi (nghe hoặc đọc)
#         skill = get_question_skill(question_id)
#         if skill == "LISTENING":
#             listening_count += 1
#
#     # Trả về kết quả
#     return JsonResponse({
#         'listening_count': listening_count,
#         'correct_answers_count': correct_answers_count,
#     })



