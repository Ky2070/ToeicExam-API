from datetime import datetime, timezone
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Authentication.models import User
from .calculate_toeic import calculate_toeic_score
from .get_question_skill import get_question_skill
from .models import Test, Part, Course, QuestionSet, Question, History
from .serializers import TestDetailSerializer, TestSerializer, PartSerializer, CourseSerializer


class QuestionSkillAPIView(APIView):
    """
    API View to retrieve the skill (LISTENING or READING) of a question by its ID.
    """
    def get(self, request, question_id):
        try:
            # Lấy câu hỏi dựa trên ID
            question = Question.objects.get(id=question_id)

            # Lấy thông tin skill từ phần mô tả
            skill = question.part.part_description.skill

            # Trả về kết quả
            return Response({'skill': skill}, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitTestView(APIView):
    def post(self, request):
        try:
            data = request.data  # Lấy dữ liệu từ body request

            # Kiểm tra định dạng dữ liệu (phải là danh sách các câu hỏi)
            if not isinstance(data, list):
                return Response({"error": "Invalid data format, expected a list of questions"}, status=status.HTTP_400_BAD_REQUEST)
            # Sử dụng get_object_or_404
            # user = get_object_or_404(User, id=user_id)

            # Sử dụng try-except
            try:
                user = User.objects.get(id=2)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Khởi tạo các biến đếm số câu hỏi đúng/sai cho listening và reading
            listening_correct = 0
            reading_correct = 0
            listening_total = 0
            reading_total = 0

            # Lưu lịch sử bắt đầu
            start_time = datetime.now(timezone.utc)

            # Duyệt qua từng câu hỏi trong dữ liệu nhận được
            for item in data:
                question_id = item.get("id")
                user_answer = item.get("user_answer")

                try:
                    # Lấy câu hỏi từ cơ sở dữ liệu
                    question = Question.objects.get(id=question_id)

                    # Kiểm tra kỹ năng của câu hỏi (Listening/Reading)
                    skill = get_question_skill(question_id)

                    # Kiểm tra câu trả lời của người dùng
                    is_correct = user_answer == question.correct_answer

                    # Cập nhật các biến đếm cho Listening hoặc Reading
                    if skill == "LISTENING":
                        listening_total += 1
                        if is_correct:
                            listening_correct += 1
                    elif skill == "READING":
                        reading_total += 1
                        if is_correct:
                            reading_correct += 1

                except Question.DoesNotExist:
                    # Nếu không tìm thấy câu hỏi trong DB, bỏ qua và tiếp tục
                    continue

            # Tính toán điểm TOEIC
            listening_score, reading_score, overall_score = calculate_toeic_score(
                listening_correct, reading_correct
            )

            # Lưu kết quả vào lịch sử bài thi
            test = Test.objects.first()  # Giả sử có một bài thi mặc định hoặc lấy từ request
            end_time = datetime.now(timezone.utc)

            history = History(
                user=user,
                test=test,
                score=overall_score,
                start_time=start_time,
                end_time=end_time,
                correct_answers=listening_correct + reading_correct,
                wrong_answers=(listening_total - listening_correct) + (reading_total - reading_correct),
                unanswer_questions=0,  # Giả sử không có câu chưa trả lời
                percentage_score=(overall_score / 100) * 100,
                listening_score=listening_score,
                reading_score=reading_score,
                complete=True,
                test_result={
                    "listening": {
                        "total_questions": listening_total,
                        "correct_answers": listening_correct,
                        "score": listening_score,
                    },
                    "reading": {
                        "total_questions": reading_total,
                        "correct_answers": reading_correct,
                        "score": reading_score,
                    },
                    "overall_score": overall_score,
                }
            )
            history.save()
            # Return response with HTTP 201 Created and a simple message
            # Trả về kết quả cho người dùng
            # Trả về kết quả với HTTP 201
            result = {
                "message": "Test submitted successfully",
                "history_id": history.id,  # Trả về ID của lịch sử
                "result": {
                    "listening": {
                        "total_questions": listening_total,
                        "correct_answers": listening_correct,
                        "score": listening_score,
                    },
                    "reading": {
                        "total_questions": reading_total,
                        "correct_answers": reading_correct,
                        "score": reading_score,
                    },
                    "overall_score": overall_score,
                }
            }
            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            # Nạp đầy đủ các phần, bộ câu hỏi, và câu hỏi liên quan đến bài kiểm tra
            test = Test.objects.prefetch_related(
                Prefetch(
                    'part_test',  # Phần trong bài kiểm tra
                    queryset=Part.objects.prefetch_related(
                        Prefetch(
                            'question_set_part',  # Bộ câu hỏi trong phần
                            queryset=QuestionSet.objects.order_by('id').prefetch_related(
                                Prefetch(
                                    'question_question_set',  # Câu hỏi trong bộ câu hỏi
                                    queryset=Question.objects.order_by('question_number')
                                )
                            )
                        ),
                        Prefetch(
                            'question_part',  # Các câu hỏi trong Part
                            queryset=Question.objects.order_by('question_number')  # Sắp xếp theo 'question_number'
                        )
                    )
                )
            ).get(pk=pk)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # Sử dụng serializer để nạp dữ liệu liên kết
        serializer = TestDetailSerializer(test)
        return Response(serializer.data)


# Bạn có thể viết một view tương tự để lấy danh sách tất cả các bài kiểm tra nếu cần:
class TestListView(APIView):
    """
    API view để lấy danh sách tất cả các bài kiểm tra đã được sắp xếp.
    """

    def get(self, request, format=None):
        # Sắp xếp các bài kiểm tra theo trường 'name' (hoặc trường bạn muốn)
        tests = Test.objects.all().order_by('id')  # hoặc 'date_created' nếu bạn muốn sắp xếp theo ngày tạo
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)


class TestPartDetailView(APIView):
    def get(self, request, test_id, part_id, format=None):
        try:
            # Tìm kiếm bài kiểm tra dựa trên `test_id`, đồng thời sắp xếp các phần liên quan
            test = Test.objects.prefetch_related(
                Prefetch(
                    'part_test',
                    queryset=Part.objects.prefetch_related(
                        Prefetch(
                            'question_set_part',  # Sắp xếp bộ câu hỏi trong phần
                            queryset=QuestionSet.objects.order_by('question_number').prefetch_related(
                                Prefetch(
                                    'question_question_set',  # Sắp xếp câu hỏi trong bộ câu hỏi
                                    queryset=Question.objects.order_by('question_number')
                                )
                            )
                        )
                    ).order_by('id')  # Sắp xếp các phần theo `id`
                )
            ).get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # Tìm kiếm phần (`part`) trong bài kiểm tra
        try:
            part = test.part_test.get(pk=part_id)
        except Part.DoesNotExist:
            return Response({"detail": "Part not found in this test."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize dữ liệu của bài kiểm tra và phần
        test_serializer = TestSerializer(test)
        part_serializer = PartSerializer(part)

        # # Kiểm tra và sắp xếp thủ công nếu cần
        # part_data = part_serializer.data
        # part_data["questionSetPart"] = sorted(
        #     part_data["questionSetPart"],
        #     key=lambda x: x["id"]
        # )
        #
        # for question_set in part_data["questionSetPart"]:
        #     question_set["questionQuestionSet"] = sorted(
        #         question_set["questionQuestionSet"],
        #         key=lambda x: x["questionNumber"]
        #     )

        return Response({
            "test": test_serializer.data,
            "part": part_serializer.data
        }, status=status.HTTP_200_OK)


class CourseListView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

# class CourseDetailView(APIView):
# def get(self, request, id):
