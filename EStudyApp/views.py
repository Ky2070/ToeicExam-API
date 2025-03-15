from datetime import datetime, timezone, timedelta
from django.db.models import Avg, Max, Min, Count
import random
from Authentication.permissions import IsTeacher
from question_bank.models import QuestionBank, QuestionSetBank
from utils.standard_part import PART_STRUCTURE


from django.db.models import Prefetch, Q
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
# from collections import defaultdict
# from EStudyApp.utils import get_cached_tests  # Import hàm cache từ utils.py

# from Authentication.models import User
from EStudyApp.calculate_toeic import calculate_toeic_score
from EStudyApp.models import PartDescription, Test, Part, QuestionSet, Question, History, QuestionType, State, TestComment, \
    HistoryTraining, Tag
from EStudyApp.serializers import HistorySerializer, HistoryTrainingSerializer, QuestionSetSerializer, \
    TestDetailSerializer, TestSerializer, \
    PartSerializer, \
    HistoryDetailSerializer, PartListSerializer, QuestionDetailSerializer, StateSerializer, TestCommentSerializer, \
    CreateTestSerializer, TestListSerializer, QuestionSerializer, TagSerializer, TestByTagSerializer, \
    StudentStatisticsSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

from EStudyApp.services.service_student import get_suggestions
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data["data"]
            test_id = request.data["test_id"]
            user = request.user

            # Lấy bài kiểm tra
            test = Test.objects.filter(id=test_id).first()
            if not test:
                return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

            # Lấy tất cả các part và skill liên quan đến test
            parts = Part.objects.filter(
                test=test).select_related('part_description')
            part_skill_map = {
                part.id: part.part_description.skill for part in parts}

            # Lấy câu hỏi từ data
            question_ids = [item.get("id") for item in data]
            questions = (Question.objects.filter(id__in=question_ids)
                         .only("id", "correct_answer", "part_id").in_bulk(field_name="id"))

            # Khởi tạo biến đếm
            listening_correct = reading_correct = listening_total = reading_total = 0
            # Giả sử timestamp gửi từ frontend dạng 'mm:ss'
            timestamp = request.data['timestamp']
            # VD: timestamp = "30:25"  # 30 phút 25 giây

            # Chuyển timestamp sang giây
            minutes, seconds = map(int, timestamp.split(":"))
            timestamp_in_seconds = 120 * 60 - (minutes * 60 + seconds)

            # start_time = datetime.now(timezone.utc)
            # end_time = start_time + timedelta(seconds=timestamp_in_seconds)
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(seconds=timestamp_in_seconds)

            for item in data:
                question_id = item.get("id")
                user_answer = item.get("user_answer")
                question = questions.get(question_id)
                item["correct_answer"] = question.correct_answer

                if question and user_answer is not None:
                    # Lấy skill từ part_skill_map
                    skill = part_skill_map.get(question.part_id)
                    is_correct = user_answer == question.correct_answer
                    if skill == "LISTENING":
                        listening_total += 1
                        if is_correct:
                            listening_correct += 1
                    elif skill == "READING":
                        reading_total += 1
                        if is_correct:
                            reading_correct += 1

            # Tính điểm TOEIC
            listening_score, reading_score, overall_score = calculate_toeic_score(
                listening_correct, reading_correct)
            correct_answers = listening_correct + reading_correct
            wrong_answers = (listening_total - listening_correct) + \
                            (reading_total - reading_correct)
            percentage_score = ((listening_correct + reading_correct) /
                                max(listening_total + reading_total, 1)) * 100
            unanswer_questions = 200 - (listening_total + reading_total)

            # Chuyển đổi QuerySet thành danh sách dictionary

            # Lưu lịch sử làm bài kiểm tra
            history = History.objects.create(
                user=user,
                test=test,
                score=overall_score,
                start_time=start_time,
                end_time=end_time,
                correct_answers=correct_answers,
                wrong_answers=wrong_answers,
                unanswer_questions=unanswer_questions,
                percentage_score=percentage_score,
                listening_score=listening_score,
                reading_score=reading_score,
                complete=True,
                test_result=data
            )

            # Tính time_taken
            time_taken = end_time - start_time

            # Chuyển đổi time_taken sang chuỗi định dạng 'mm:ss'
            minutes, seconds = divmod(time_taken.total_seconds(), 60)
            formatted_time_taken = f"{int(minutes):02}:{int(seconds):02}"

            result = {
                "message": "Test submitted successfully",
                "history_id": history.id,
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
                    "unanswer_questions": unanswer_questions,
                    "overall_score": overall_score,
                    "time_taken": formatted_time_taken
                }
            }

            state = State.objects.filter(
                user=user, test=test).order_by('-id').first()
            if state:
                state.used = True
                state.save()
            else:
                pass

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        user = request.user
        histories = History.objects.filter(user=user)
        serializer = HistorySerializer(histories, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailHistoryView(APIView):
    is_authenticated = [IsAuthenticated]

    def get(self, request, history_id):
        user = request.user
        user_id = user.id
        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        history = History.objects.filter(
            id=history_id, user_id=user_id).first()

        if history is None:
            return Response({"error": "History not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HistoryDetailSerializer(history, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailSubmitTestView(APIView):
    # Chỉ cho phép người dùng đã xác thực
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id  # Lấy ID của người dùng hiện tại
        test_id = request.GET.get('test_id')
        if test_id is None:
            return Response({"error": "Test ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        test = Test.objects.get(id=test_id)
        if test is None:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

        # Truy vấn dữ liệu History và chỉ lấy các trường cần thiết
        histories = (
            History.objects.filter(user_id=user_id, test=test)
            .select_related('test')  # Join bảng Test
            .only(
                'id', 'user_id', 'score', 'start_time', 'end_time',
                'listening_score', 'reading_score',  # Trường từ History
                'complete', 'test__id', 'test__name'  # Chỉ lấy id và name từ Test
            )
        )

        if not histories.exists():
            return Response(
                {"error": "No history found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize danh sách lịch sử
        serializer = HistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TestDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            # Nạp đầy đủ các phần, bộ câu hỏi, và câu hỏi liên quan đến bài kiểm tra
            test = Test.objects.prefetch_related(
                Prefetch(
                    'part_test',  # Phần trong bài kiểm tra
                    queryset=Part.objects.order_by('part_description__part_number').prefetch_related(
                        Prefetch(
                            'question_set_part',  # Bộ câu hỏi trong phần
                            queryset=QuestionSet.objects.order_by('id').prefetch_related(
                                Prefetch(
                                    'question_question_set',  # Câu hỏi trong bộ câu hỏi
                                    queryset=Question.objects.order_by(
                                        'question_number')
                                )
                            )
                        ),
                        Prefetch(
                            'question_part',  # Các câu hỏi trong Part
                            # Sắp xếp theo 'question_number'
                            queryset=Question.objects.filter(test_id=pk).order_by(
                                'question_number')
                        )
                    )
                ),
                Prefetch(
                    'question_test',
                    queryset=Question.objects.order_by('question_number')
                )
            ).get(pk=pk)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # Sử dụng serializer để nạp dữ liệu liên kết
        serializer = TestDetailSerializer(test)
        return Response(serializer.data)


class FixedTestPagination(PageNumberPagination):
    """
    Phân trang với giới hạn cố định 6 bài kiểm tra mỗi trang.
    """
    page_size = 6  # Số lượng bài kiểm tra mỗi trang (không thể thay đổi)
    page_size_query_param = None  # Không cho phép người dùng thay đổi số lượng
    max_page_size = 6  # Giới hạn cứng


class TestListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    """
       API view để lấy danh sách các bài kiểm tra với phân trang cố định.
    """

    def get(self, request, format=None):
        # Lấy danh sách bài kiểm tra, tránh truy vấn toàn bộ cơ sở dữ liệu
        # get type from request and default is Practice
        if request.GET.get('type') is None:
            tests = Test.objects.all()
            serializer = TestSerializer(tests, many=True)
            return Response(serializer.data)

        type = request.GET.get('type') if request.GET.get(
            'type') is not None else 'Practice'

        tests = Test.objects.prefetch_related(
            Prefetch(
                'part_test',
                queryset=Part.objects.all()
            ),
            Prefetch(
                'history_test',
                queryset=History.objects.order_by('-end_time'),
                to_attr='user_histories'
            )
        ).filter(publish=True, types=type).select_related(
            'tag').order_by('id')  # Sắp xếp theo `id`
        paginator = FixedTestPagination()  # Sử dụng phân trang cố định
        paginated_tests = paginator.paginate_queryset(
            tests, request)  # Phân trang dữ liệu
        serializer = TestSerializer(paginated_tests, many=True)
        # Trả dữ liệu kèm thông tin phân trang
        return paginator.get_paginated_response(serializer.data)

    # def get(self, request, format=None):
    #     # Sắp xếp các bài kiểm tra theo trường 'name' (hoặc trường bạn muốn)
    #     # hoặc 'date_created' nếu bạn muốn sắp xếp theo ngày tạo
    #     tests = Test.objects.all().select_related('tag').order_by('id')
    #     serializer = TestSerializer(tests, many=True)
    #     return Response(serializer.data)


class TestPartDetailView(APIView):
    def get(self, request, test_id, format=None):
        parts = [int(part) for part in request.GET.get('parts').split(',')]
        try:
            # Tìm kiếm bài kiểm tra dựa trên `test_id`, đồng thời sắp xếp các phần liên quan
            test = Test.objects.prefetch_related(
                Prefetch(
                    'part_test',
                    queryset=Part.objects.filter(id__in=parts).order_by('part_description__part_number').prefetch_related(
                        Prefetch(
                            'question_set_part',  # Sắp xếp bộ câu hỏi trong phần
                            queryset=QuestionSet.objects.order_by('id').prefetch_related(
                                Prefetch(
                                    'question_question_set',  # S���p xếp câu hỏi trong bộ câu hỏi
                                    queryset=Question.objects.filter(
                                        part_id__in=parts).order_by(
                                        'question_number')
                                )
                            )
                        )
                    ).order_by('part_description__part_number')  # Sắp xếp các phần theo `id`
                ),
                Prefetch(
                    'question_test',
                    queryset=Question.objects.filter(
                        part_id__in=parts).order_by('question_number')
                )
            ).get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestDetailSerializer(test)
        return Response(serializer.data)


# class CourseListView(APIView):
#     def get(self, request):
#         courses = Course.objects.all()
#         serializer = CourseSerializer(courses, many=True)
#         return Response(serializer.data)


class PartListView(APIView):
    def get(self, request, test_id):
        parts = Part.objects.filter(test=test_id).select_related(
            'part_description').order_by('id')

        serializer = PartListSerializer(parts, many=True)
        return Response(serializer.data)


class StateCreateView(APIView):
    # Chỉ cho phép người dùng đã đăng nhập
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Lấy user từ request
        user = request.user
        test = Test.objects.filter(id=request.data.get('test_id')).first()

        state = State.objects.filter(
            user=user, test=test).order_by('-id').first()

        if state and state.used == False:
            return Response(
                {"detail": "State is already created."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Thêm user vào dữ liệu được gửi từ client

        info = request.data["info"]
        initial_minutes = 120
        initial_seconds = 0

        state = State.objects.create(
            user=user,
            test=test,
            info=info,
            initial_minutes=initial_minutes,
            initial_seconds=initial_seconds,
            name='Test State',
            used=False
        )

        serializer = StateSerializer(state, many=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        user = request.user
        test = Test.objects.filter(id=request.data.get('test_id')).first()
        initial_minutes = request.data.get('initial_minutes')
        initial_seconds = request.data.get('initial_seconds')
        minutes = (120 - initial_minutes) * 60
        seconds = (60 - initial_seconds)
        time_taken = minutes + seconds

        state = State.objects.filter(
            user=user, test=test, used=False).order_by('-id').first()

        if not state:
            return Response(
                {"detail": "No state found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )

        state.info = request.data["info"]
        state.initial_minutes = initial_minutes
        state.initial_seconds = initial_seconds
        state.time_taken = time_taken
        state.save()

        serializer = StateSerializer(state, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TestCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # data = request.data["data"]
        # test_id = request.data["test_id"]
        # parent_id = request.data["parent_id"]
        content = request.data.get("content")  # Nội dung comment
        test_id = request.data.get("test_id")  # ID của bài kiểm tra
        # ID của comment cha (nếu là reply)
        parent_id = request.data.get("parent_id")

        if not content:
            return Response({"detail": "Comment content is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not test_id:
            return Response({"detail": "Test ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra comment cha
        parent = None
        if parent_id:
            try:
                parent = TestComment.objects.get(id=parent_id, test_id=test_id)
            except TestComment.DoesNotExist:
                return Response({"detail": "Parent comment not found or does not belong to this test."},
                                status=status.HTTP_404_NOT_FOUND)
        # Chuẩn bị dữ liệu để post comment
        try:
            comment = TestComment.objects.create(
                user=user,
                test=test,
                parent=parent,
                content=content
            )
            comment.save()
            serializer = TestCommentSerializer(comment, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Cập nhật một phần nội dung bình luận.
        """
        user = request.user
        data = request.data  # Payload từ yêu cầu

        try:
            comment = TestComment.objects.get(id=pk, user=user)
        except TestComment.DoesNotExist:
            return Response(
                {"detail": "Comment not found or you are not authorized to edit this comment."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Cập nhật với serializer
        serializer = TestCommentSerializer(comment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa một comment và tất cả các comment con (nếu có).
        """
        user = request.user

        try:
            # Lấy comment dựa vào ID và đảm bảo user là chủ sở hữu
            comment = TestComment.objects.get(id=pk, user=user)
        except TestComment.DoesNotExist:
            return Response(
                {"detail": "Comment not found or you are not authorized to delete this comment."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Xóa tất cả các comment con liên quan
        child_comments = TestComment.objects.filter(parent=comment)
        for child in child_comments:
            child.delete()

        # Xóa comment cha
        comment.delete()

        return Response({"detail": "Comment and its children deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    def get(self, request, test_id):
        """
        Lấy danh sách comment trong một bài kiểm tra.
        """
        # Kiểm tra bài kiểm tra có tồn tại không
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response(
                {"detail": "Test not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Lấy tất cả comment thuộc về bài kiểm tra này
        comments = TestComment.objects.filter(
            test=test, parent=None).order_by("-publish_date")

        # Serialize dữ liệu
        serializer = TestCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Lấy state mới nhất
        state = State.objects.filter(
            user=user, used=False).order_by('-id').first()
        # convert state.created_at - date now to seconds
        created_at = state.created_at
        now = datetime.now(timezone.utc)
        time_taken = now - created_at
        minutes, seconds = divmod(time_taken.total_seconds(), 60)
        state.initial_minutes = 120 - minutes
        state.initial_seconds = 60 - seconds
        state.time_taken = minutes + seconds
        state.save()

        # # convert time to seconds
        # time_taken = state.time
        # minutes, seconds = divmod(time_taken.total_seconds(), 60)
        # formatted_time_taken = f"{int(minutes):02}:{int(seconds):02}"

        if not state:
            return Response(
                {"detail": "No state found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize state
        serializer = StateSerializer(state)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchTestsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query_param = request.GET.get('q', '').strip()
        if not query_param:
            return Response({"error": "Query parameter 'q' is required."}, status=400)

        # # Tách từ khóa thành danh sách và tìm kiếm tất cả các từ
        # search_terms = query_param.split()
        # query = SearchQuery(' & '.join(search_terms), search_type='plain')
        #
        # # Tìm kiếm trong trường 'name'
        # tests = Test.objects.annotate(
        #     search=SearchVector('name', config='english')
        # ).filter(search=query)

        # Tìm kiếm theo name hoặc tag (case-insensitive)
        tests = Test.objects.filter(
            Q(name__icontains=query_param) | Q(
                tag__name__icontains=query_param)
        )

        # Chuyển đổi kết quả sang JSON
        result = [
            {
                "id": test.id,
                "name": test.name,
                "description": test.description,
                "type": test.type,
                "testDate": test.test_date.strftime('%Y-%m-%d %H:%M:%S') if test.test_date else None,
                "duration": str(test.duration) if test.duration else None,
                "questionCount": test.question_count,
                "partCount": test.part_count,
                "tag": test.tag.name if test.tag else None,
            }
            for test in tests
        ]

        return Response(result)


class SubmitTrainingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            test_id = request.data['test_id']
            data = request.data['data']
            timestamp = request.data['timestamp']

            # Chuyển timestamp sang giây
            minutes, seconds = map(int, timestamp.split(":"))
            timestamp_in_seconds = minutes * 60 + seconds

            start_time = datetime.now(timezone.utc)
            end_time = start_time + timedelta(seconds=timestamp_in_seconds)

            # Kiểm tra Test
            test = Test.objects.filter(id=test_id).first()
            if not test:
                return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

            # Lấy tất cả `part_id` và `question_id` từ data
            part_ids = {item.get("part_id") for item in data}
            question_ids = {item.get("id") for item in data}

            # Truy vấn tất cả Part trong một lần
            parts = Part.objects.filter(
                id__in=part_ids).in_bulk(field_name="id")
            missing_parts = part_ids - set(parts.keys())
            if missing_parts:
                return Response({"error": f"Parts not found: {', '.join(map(str, missing_parts))}"},
                                status=status.HTTP_404_NOT_FOUND)

            # Truy vấn tất cả các Question liên quan
            questions = (
                Question.objects.filter(
                    id__in=question_ids, part_id__in=part_ids)
                .only("id", "correct_answer", "part_id")
                .in_bulk(field_name="id")
            )
            missing_questions = question_ids - set(questions.keys())
            if missing_questions:
                return Response({"error": f"Questions not found: {', '.join(map(str, missing_questions))}"},
                                status=status.HTTP_404_NOT_FOUND)

            # Xử lý câu hỏi và tính toán kết quả
            total_correct_answers = 0
            total_wrong_answers = 0
            total_unanswer_questions = 0
            part_results = []

            # Danh sách part đã xử lý
            processed_parts = []

            for part_id in part_ids:
                part = parts.get(part_id)
                if not part:
                    continue

                correct_answers = 0
                wrong_answers = 0
                unanswer_questions = 0

                for item in filter(lambda x: x.get("part_id") == part_id, data):
                    question_id = item.get("id")
                    user_answer = item.get("user_answer")
                    question = questions.get(question_id)
                    item["correct_answer"] = question.correct_answer

                    if not question:
                        continue  # Bỏ qua nếu câu hỏi không hợp lệ

                    if user_answer is None:
                        unanswer_questions += 1
                    elif user_answer == question.correct_answer:
                        correct_answers += 1
                    else:
                        wrong_answers += 1

                # Tính toán điểm phần
                total_questions = correct_answers + wrong_answers
                percentage_score = (
                    correct_answers / total_questions) * 100 if total_questions > 0 else 0

                # Cập nhật kết quả tổng hợp
                total_correct_answers += correct_answers
                total_wrong_answers += wrong_answers
                total_unanswer_questions += unanswer_questions

                # Lưu thông tin part đã xử lý
                processed_parts.append(part.id)

                part_results.append({
                    "part_id": part.id,
                    "correct_answers": correct_answers,
                    "wrong_answers": wrong_answers,
                    "unanswer_questions": unanswer_questions,
                    "percentage_score": percentage_score,
                })

            # Tính toán tổng kết điểm
            total_questions = total_correct_answers + total_wrong_answers
            overall_percentage_score = (
                total_correct_answers / total_questions) * 100 if total_questions > 0 else 0

            # Tính thời gian thực hiện
            time_taken = end_time - start_time
            minutes, seconds = divmod(time_taken.total_seconds(), 60)
            formatted_time_taken = f"{int(minutes):02}:{int(seconds):02}"

            # Lưu kết quả tổng vào `HistoryTraining`
            history = HistoryTraining.objects.create(
                user=user,
                test=test,
                start_time=start_time,
                end_time=end_time,
                correct_answers=total_correct_answers,
                wrong_answers=total_wrong_answers,
                unanswer_questions=total_unanswer_questions,
                percentage_score=overall_percentage_score,
                complete=True,
                test_result=data,
                # Lưu danh sách part_id vào part_list
                part_list=",".join(map(str, processed_parts))
            )

            # Trả về kết quả tổng hợp
            result = {
                "message": "Training submitted successfully",
                "overall_result": {
                    "total_correct_answers": total_correct_answers,
                    "total_wrong_answers": total_wrong_answers,
                    "total_unanswer_questions": total_unanswer_questions,
                    "overall_percentage_score": overall_percentage_score,
                },
                "part_results": part_results,
                "time_taken": formatted_time_taken,
                "history_id": history.id,
            }

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        test_id = request.GET.get('test_id')
        test = Test.objects.get(id=test_id)
        if not test:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        history = HistoryTraining.objects.filter(
            user=user, test=test).order_by('-id')
        serializer = HistoryTrainingSerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailTrainingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, history_id):
        print(history_id)
        history = HistoryTraining.objects.get(id=history_id)
        if not history:
            return Response({"error": "History not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HistoryTrainingSerializer(history, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListTestView(APIView):
    # Chỉ người dùng đã đăng nhập mới được phép truy cập
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Lấy danh sách bài kiểm tra.
        """
        tests = Test.objects.all().order_by(
            '-id')  # Lấy tất cả các bài kiểm tra từ cơ sở dữ liệu
        # Sử dụng serializer để chuyển đổi dữ liệu
        serializer = TestListSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Tạo đề thi
class TestCreateAPIView(APIView):
    # Chỉ người dùng đã đăng nhập mới được phép truy cập
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateTestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id, *args, **kwargs):
        """
        Lấy thông tin chi tiết bài thi theo ID.
        """
        try:
            test = Test.objects.get(id=id)
            serializer = TestListSerializer(test)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)


class TestUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Chỉ người dùng đã đăng nhập

    def put(self, request, id, *args, **kwargs):
        """
            Cập nhật thông tin bài thi theo ID.
            """
        try:
            test = Test.objects.get(id=id)
            serializer = CreateTestSerializer(
                test, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)


class TestDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Chỉ người dùng đã đăng nhập

    def delete(self, request, id, *args, **kwargs):
        """
            Xóa bài thi theo ID.
            """
        try:
            test = Test.objects.get(id=id)
            test.delete()
            return Response({'message': 'Test deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)


class TestQuestionSetAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, id, *args, **kwargs):
        try:
            test = Test.objects.get(id=id)
            question_set = QuestionSet.objects.filter(
                test=test).order_by('from_ques')
            serializer = QuestionSetSerializer(question_set, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetPartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None, *args, **kwargs):
        """
        Lấy danh sách tất cả hoặc thông tin chi tiết của một phần (Part).
        """
        if id:
            try:
                part = Part.objects.get(id=id)
                serializer = PartListSerializer(part)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Part.DoesNotExist:
                return Response({'error': 'Part not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            parts = Part.objects.all().order_by('-id')
            serializer = PartListSerializer(parts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class PartListQuestionsSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _process_answers(self, answers):
        """Helper method to uppercase answer values"""
        if not answers:
            return answers
        return {
            key.upper(): value if isinstance(value, str) else value
            for key, value in answers.items()
        }

    def get(self, request, part_id, *args, **kwargs):
        part = Part.objects.get(id=part_id)
        if not part:
            return Response({"error": "Part not found"}, status=status.HTTP_404_NOT_FOUND)

        questions_set = QuestionSet.objects.filter(
            part=part).order_by('from_ques')

        serializer = QuestionSetSerializer(questions_set, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, part_id, *args, **kwargs):
        data = request.data
        question_set_id = data.get('id')
        audio = data.get('audio')
        page = data.get('page')
        image = data.get('image')
        from_ques = data.get('from_ques')
        to_ques = data.get('to_ques')
        question_question_set = data.get('question_question_set', [])
        test_id = data.get('test_id')
        test = Test.objects.get(id=test_id)

        try:
            # get part
            part = Part.objects.get(id=part_id)

            # get question set
            question_set = None

            if question_set_id:
                question_set = QuestionSet.objects.get(id=question_set_id)
                question_set.audio = audio
                question_set.page = page
                question_set.image = image
                question_set.from_ques = int(from_ques)
                question_set.to_ques = int(to_ques)
                question_set.test = test
                question_set.save()
            else:
                question_set = QuestionSet.objects.create(
                    part=part,
                    audio=audio,
                    page=page,
                    image=image,
                    from_ques=int(from_ques),
                    to_ques=int(to_ques),
                    test=test,
                )
                question_set_id = question_set.id

            # Create a set of incoming question IDs
            # incoming_question_ids = {
            #     q.get('id') for q in question_question_set if q.get('id')}

            # Create a dictionary of incoming questions for updates
            question_updates = {
                q.get('id'): q for q in question_question_set if q.get('id')
            }

            question_add = [
                q for q in question_question_set if q.get('id') is None]

            # Delete questions that are not in the incoming set
            question_not_delete = [
                q for q in question_question_set if q.get('id') is not None]
            Question.objects.filter(question_set=question_set).exclude(
                id__in=[question['id'] for question in question_not_delete]).delete()

            # Get existing questions
            existing_questions = Question.objects.filter(
                question_set=question_set)

            # Update existing questions
            for question in existing_questions:
                if question.id in question_updates:
                    update_data = question_updates[question.id]
                    question.question_text = update_data.get(
                        'question_text', question.question_text)
                    # Uppercase the answers
                    answers = update_data.get('answers')
                    question.answers = self._process_answers(answers)
                    question.correct_answer = update_data.get(
                        'correct_answer', '').upper()
                    question.question_number = update_data.get(
                        'question_number', question.question_number)
                    question.difficulty_level = update_data.get(
                        'difficulty_level', question.difficulty_level)
                    question.test = test
                    question.part = part
                    question.save()
                    del question_updates[question.id]

            # Create new questions for any remaining in question_updates
            for new_question_data in question_add:
                Question.objects.create(
                    question_set=question_set,
                    part=part,
                    question_text=new_question_data.get('question_text'),
                    # Uppercase the answers for new questions
                    answers=self._process_answers(
                        new_question_data.get('answers')),
                    correct_answer=new_question_data.get(
                        'correct_answer', '').upper(),
                    question_number=new_question_data.get('question_number'),
                    difficulty_level=new_question_data.get('difficulty_level'),
                    test=test,
                )

            # Refresh and serialize the updated question set
            question_set_data = QuestionSet.objects.get(id=question_set_id)
            serializer = QuestionSetSerializer(question_set_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Part.DoesNotExist:
            return Response({"error": "Part not found"}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EditQuestionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _process_answers(self, answers):
        """Helper method to uppercase answer values"""
        if not answers:
            return answers
        return {
            key.upper(): value if isinstance(value, str) else value
            for key, value in answers.items()
        }

    def put(self, request, part_id, question_set_id, *args, **kwargs):
        data = request.data
        audio = data.get('audio')
        page = data.get('page')
        image = data.get('image')
        from_ques = data.get('from_ques')
        to_ques = data.get('to_ques')
        question_question_set = data.get('question_question_set', [])

        try:
            # get part
            part = Part.objects.get(id=part_id)

            # get question set
            question_set = QuestionSet.objects.get(id=question_set_id)
            if question_set:
                # update question set basic info
                question_set.audio = audio
                question_set.page = page
                question_set.image = image
                question_set.from_ques = int(from_ques)
                question_set.to_ques = int(to_ques)
                question_set.save()
            else:
                if data.get('id') is None:
                    question_set = QuestionSet.objects.create(
                        part=part,
                        audio=audio,
                        page=page,
                        image=image,
                        from_ques=int(from_ques),
                        to_ques=int(to_ques),
                    )
                else:
                    return Response({"error": "Question set not found"}, status=status.HTTP_404_NOT_FOUND)

            # Create a set of incoming question IDs
            # incoming_question_ids = {
            #     q.get('id') for q in question_question_set if q.get('id')}

            # Create a dictionary of incoming questions for updates
            question_updates = {
                q.get('id'): q for q in question_question_set if q.get('id')
            }

            question_add = [
                q for q in question_question_set if q.get('id') is None]

            # Delete questions that are not in the incoming set
            question_not_delete = [
                q for q in question_question_set if q.get('id') is not None]
            Question.objects.filter(question_set=question_set).exclude(
                id__in=[question['id'] for question in question_not_delete]).delete()

            # Get existing questions
            existing_questions = Question.objects.filter(
                question_set=question_set)

            # Update existing questions
            for question in existing_questions:
                if question.id in question_updates:
                    update_data = question_updates[question.id]
                    question.question_text = update_data.get(
                        'question_text', question.question_text)
                    # Uppercase the answers
                    answers = update_data.get('answers')
                    question.answers = self._process_answers(answers)
                    question.correct_answer = update_data.get(
                        'correct_answer', '').upper()
                    question.question_number = update_data.get(
                        'question_number', question.question_number)
                    question.difficulty_level = update_data.get(
                        'difficulty_level', question.difficulty_level)
                    question.save()
                    del question_updates[question.id]

            # Create new questions for any remaining in question_updates
            for new_question_data in question_add:
                Question.objects.create(
                    question_set=question_set,
                    part=part,
                    question_text=new_question_data.get('question_text'),
                    # Uppercase the answers for new questions
                    answers=self._process_answers(
                        new_question_data.get('answers')),
                    correct_answer=new_question_data.get(
                        'correct_answer', '').upper(),
                    question_number=new_question_data.get('question_number'),
                    difficulty_level=new_question_data.get('difficulty_level'),
                )

            # Refresh and serialize the updated question set
            question_set_data = QuestionSet.objects.get(id=question_set_id)
            serializer = QuestionSetSerializer(question_set_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Part.DoesNotExist:
            return Response({"error": "Part not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreatePartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id, *args, **kwargs):
        """
        Tạo một phần (Part) mới.
        """
        part_number = request.data['part']

        test = Test.objects.get(id=test_id)
        partDescription = PartDescription.objects.filter(
            part_name=f"Part {part_number}",
        ).first()

        existing_part = Part.objects.filter(
            part_description=partDescription, test=test).first()
        if existing_part:
            return Response({"error": "Part already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if not test:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

        if not partDescription:
            return Response({"error": "Part description not found"}, status=status.HTTP_404_NOT_FOUND)

        part = Part.objects.create(
            part_description=partDescription,
            test=test,
        )

        serializer = PartListSerializer(part)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, test_id, *args, **kwargs):
        test = Test.objects.get(id=test_id)
        if not test:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)
        parts = Part.objects.filter(test=test).order_by(
            'part_description__part_number')
        serializer = PartListSerializer(parts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePartAutoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _create_part(self, part_number, test, part_description, part):
        try:
            # Save the part instance first to get a primary key
            part.save()

            part_structures = PART_STRUCTURE[f'PART_{part_number}']
            for from_ques, to_ques in part_structures['sets']:
                existing_question_sets = QuestionSetBank.objects.filter(
                    from_ques=from_ques,
                    to_ques=to_ques,
                )  # Prefetch related questions

                # random divide existing_question_sets
                random_question_set = random.choice(existing_question_sets)

                # Create new question set
                new_question_set = QuestionSet.objects.create(
                    part=part,
                    from_ques=from_ques,
                    to_ques=to_ques,
                    audio=random_question_set.audio,
                    page=random_question_set.page,
                    image=random_question_set.image,
                    test=test,
                )

                # Duplicate questions
                existing_questions = QuestionBank.objects.filter(
                    question_set=random_question_set)
                for question in existing_questions:
                    Question.objects.create(
                        question_set=new_question_set,
                        part=part,
                        test=test,
                        question_text=question.question_text,
                        answers=question.answers,
                        correct_answer=question.correct_answer,
                        question_number=question.question_number,
                        difficulty_level=question.difficulty_level,
                    )

            return part

        except Exception as e:
            # If anything fails, delete the part and raise the error
            if part.id:
                part.delete()
            raise e

    def post(self, request, test_id, *args, **kwargs):
        try:
            part_number = request.data['part']
            # check if part is exist
            part_description = PartDescription.objects.get(
                part_name=f"Part {part_number}")
            part = Part.objects.filter(
                part_description=part_description, test_id=test_id).first()
            if part:
                return Response({"error": "Part already exists"}, status=status.HTTP_400_BAD_REQUEST)

            test = Test.objects.get(id=test_id)

            if not test:
                return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

            if not part_description:
                return Response({"error": "Part description not found"}, status=status.HTTP_404_NOT_FOUND)

            new_part = Part(
                part_description=part_description,
                test=test,
            )

            created_part = self._create_part(
                part_number, test, part_description, new_part)
            serializer = PartListSerializer(created_part)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdatePartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id, *args, **kwargs):
        """
        Cập nhật thông tin một phần (Part) theo ID.
        """
        try:
            part = Part.objects.get(id=id)
            serializer = PartListSerializer(
                part, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Part.DoesNotExist:
            return Response({'error': 'Part not found'}, status=status.HTTP_404_NOT_FOUND)


class DeletePartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id, *args, **kwargs):
        """
        Delete Part and all related objects by ID.
        """
        try:
            # Get the part
            part = Part.objects.get(id=id)

            # Serialize the part data before deletion
            serializer = PartListSerializer(part)
            response_data = serializer.data

            # Delete the part after serializing
            part.delete()

            # Return the serialized data of the deleted part
            return Response(response_data, status=status.HTTP_200_OK)

        except Part.DoesNotExist:
            return Response({'error': 'Part not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = (Question.objects.filter(deleted_at__isnull=True)
                     .select_related('question_type')
                     .order_by('id'))

        # .only('id',
        #       'question_number',
        #       'question_text',
        #       'answers',
        #       'question_type__id',
        #       'question_type__name'
        #       )
        # Kiểm tra nếu queryset trống
        if not questions.exists():
            return Response({"detail": "No questions found."}, status=status.HTTP_404_NOT_FOUND)

        # Sử dụng serializer để chuyển đổi queryset thành dữ liệu JSON
        serializer = QuestionDetailSerializer(questions, many=True)
        return Response(serializer.data)


class CreateQuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
               Tạo một câu hỏi mới.
               """
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailQuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        """
        Lấy chi tiết một câu hỏi theo ID.
        """
        try:
            question = Question.objects.get(id=id, deleted_at__isnull=True)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found or Question deleted'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionDetailSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateQuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id, *args, **kwargs):
        """
        Cập nhật thông tin câu hỏi theo ID.
        """
        try:
            question = Question.objects.get(id=id, deleted_at__isnull=True)
            serializer = QuestionDetailSerializer(
                question, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found or Question deleted'}, status=status.HTTP_404_NOT_FOUND)


class DeleteQuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id, *args, **kwargs):
        """
        Xóa một câu hỏi theo ID.
        """
        try:
            question = Question.objects.get(id=id)
            question.delete()
            serializer = QuestionDetailSerializer(question)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)


class StudentStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Yêu cầu đăng nhập

    def get(self, request, *args, **kwargs):
        user = request.user
        stats = {
            "avg_score": History.objects.filter(user=user).aggregate(Avg('score'))['score__avg'],
            "max_score": History.objects.filter(user=user).aggregate(Max('score'))['score__max'],
            "min_score": History.objects.filter(user=user).aggregate(Min('score'))['score__min'],
            "total_tests": History.objects.filter(user=user, complete=True).count(),
        }
        serializer = StudentStatisticsSerializer(stats)
        return Response(serializer.data)


class SystemStatisticsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        stats = {
            "total_tests": Test.objects.count(),
            "total_completed_tests": History.objects.filter(complete=True).count(),
            "avg_score": History.objects.aggregate(Avg('score'))['score__avg'],
        }
        return Response(stats)


class StudentReportView(APIView):
    def get(self, request, user_id):
        history = History.objects.filter(user_id=user_id, complete=True)
        training = HistoryTraining.objects.filter(user_id=user_id, complete=True)

        history_data = HistorySerializer(history, many=True).data
        training_data = HistoryTrainingSerializer(training, many=True).data

        analysis = get_suggestions(user_id)

        return Response({
            "history": history_data,
            "training": training_data,
            "analysis": analysis
        }, status=status.HTTP_200_OK)