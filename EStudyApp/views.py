from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .calculate_toeic import calculate_toeic_score
from .get_question_skill import get_question_skill
from .models import Test, Part, Course, QuestionSet, Question
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


class QuestionSkillAnalysisView(APIView):
    def post(self, request):
        try:
            data = request.data  # Lấy dữ liệu từ body request
            if not isinstance(data, list):
                return Response({"error": "Invalid data format, expected a list of questions"}, status=status.HTTP_400_BAD_REQUEST)

            # Tạo các biến đếm
            listening_correct = 0
            reading_correct = 0
            listening_total = 0
            reading_total = 0
            print("Request data:", data)
            for item in data:
                print("Processing item:", item)
                question_id = item.get("id")
                question_number = item.get("question_number")
                user_answer = item.get("user_answer")
                print(question_id)
                print(f'Câu hỏi số : {question_number}')
                try:
                    # Lấy câu hỏi từ database
                    question = Question.objects.get(id=question_id)
                    # Kiểm tra kỹ năng của câu hỏi
                    skill = get_question_skill(question_id)
                    print(skill)
                    # So sánh câu trả lời của người dùng với câu trả lời đúng
                    is_correct = user_answer == question.correct_answer
                    print(user_answer)
                    print(question.correct_answer)
                    print(is_correct)
                    # Cập nhật số lượng theo kỹ năng
                    if skill == "LISTENING":
                        listening_total += 1
                        if is_correct:
                            listening_correct += 1
                    elif skill == "READING":
                        reading_total += 1
                        if is_correct:
                            reading_correct += 1

                except Question.DoesNotExist:
                    # Nếu không tìm thấy câu hỏi, bỏ qua
                    continue

                # Tính điểm TOEIC
                listening_score, reading_score, overall_score = calculate_toeic_score(
                    listening_correct, reading_correct
                )

                # Trả về kết quả
                result = {
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

            return Response(result, status=status.HTTP_200_OK)

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
