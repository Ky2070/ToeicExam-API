from datetime import datetime, timezone
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from EStudyApp.utils import get_cached_tests  # Import hàm cache từ utils.py

# from Authentication.models import User
from EStudyApp.calculate_toeic import calculate_toeic_score
from EStudyApp.models import Test, Part, Course, QuestionSet, Question, History, QuestionType, State, TestComment
from EStudyApp.serializers import HistorySerializer, TestDetailSerializer, TestSerializer, PartSerializer, \
    CourseSerializer, \
    HistoryDetailSerializer, PartListSerializer, QuestionDetailSerializer, StateSerializer, TestCommentSerializer
from rest_framework.permissions import IsAuthenticated


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
            parts = Part.objects.filter(test=test).select_related('part_description')
            part_skill_map = {part.id: part.part_description.skill for part in parts}

            # Lấy câu hỏi từ data
            question_ids = [item.get("id") for item in data]
            questions = (Question.objects.filter(id__in=question_ids)
                         .only("id", "correct_answer", "part_id").in_bulk(field_name="id"))

            # Khởi tạo biến đếm
            listening_correct = reading_correct = listening_total = reading_total = 0
            start_time = datetime.now(timezone.utc)
            end_time = datetime.now(timezone.utc)
            for item in data:
                question_id = item.get("id")
                user_answer = item.get("user_answer")
                question = questions.get(question_id)

                if question:
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
            listening_score, reading_score, overall_score = calculate_toeic_score(listening_correct, reading_correct)
            correct_answers = listening_correct + reading_correct
            wrong_answers = (listening_total - listening_correct) + (reading_total - reading_correct)
            percentage_score = ((listening_correct + reading_correct) / max(listening_total + reading_total, 1)) * 100
            unanswer_questions = 200 - (listening_total + reading_total)

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
                }
            }

            state = State.objects.filter(user=user, test=test).order_by('-id').first()
            if state:
                state.used = True
                state.save()
            else:
                pass

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
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

        history = History.objects.filter(id=history_id, user_id=user_id).first()

        if history is None:
            return Response({"error": "History not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HistoryDetailSerializer(history, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailSubmitTestView(APIView):
    permission_classes = [IsAuthenticated]  # Chỉ cho phép người dùng đã xác thực

    def get(self, request):
        user_id = request.user.id  # Lấy ID của người dùng hiện tại

        # Truy vấn dữ liệu History và chỉ lấy các trường cần thiết
        histories = (
            History.objects.filter(user_id=user_id)
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
                    queryset=Part.objects.prefetch_related(
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
                            queryset=Question.objects.order_by(
                                'question_number')
                        )
                    )
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
    """
       API view để lấy danh sách các bài kiểm tra với phân trang cố định.
    """

    def get(self, request, format=None):
        # Lấy danh sách bài kiểm tra, tránh truy vấn toàn bộ cơ sở dữ liệu
        tests = Test.objects.all().select_related('tag').order_by('id')  # Sắp xếp theo `id`
        paginator = FixedTestPagination()  # Sử dụng phân trang cố định
        paginated_tests = paginator.paginate_queryset(tests, request)  # Phân trang dữ liệu
        serializer = TestSerializer(paginated_tests, many=True)
        return paginator.get_paginated_response(serializer.data)  # Trả dữ liệu kèm thông tin phân trang

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
                    queryset=Part.objects.filter(id__in=parts).prefetch_related(
                        Prefetch(
                            'question_set_part',  # Sắp xếp bộ câu hỏi trong phần
                            queryset=QuestionSet.objects.order_by('id').prefetch_related(
                                Prefetch(
                                    'question_question_set',  # Sắp xếp câu hỏi trong bộ câu hỏi
                                    queryset=Question.objects.order_by(
                                        'question_number')
                                )
                            )
                        )
                    ).order_by('id')  # Sắp xếp các phần theo `id`
                )
            ).get(pk=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestDetailSerializer(test)
        return Response(serializer.data)


class CourseListView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class PartListView(APIView):
    def get(self, request, test_id):
        parts = Part.objects.filter(test=test_id).select_related('part_description').order_by('id')

        serializer = PartListSerializer(parts, many=True)
        return Response(serializer.data)


class QuestionListView(APIView):
    def get(self, request):
        questions = (Question.objects.all()
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


class StateCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Chỉ cho phép người dùng đã đăng nhập

    def post(self, request):
        # Lấy user từ request
        user = request.user
        test = Test.objects.filter(id=request.data.get('test_id')).first()

        state = State.objects.filter(user=user, test=test).order_by('-id').first()

        if state and state.used == False:
            return Response(
                {"detail": "State is already created."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Thêm user vào dữ liệu được gửi từ client

        info = request.data["info"]
        initial_minutes = 0
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

        state = State.objects.filter(user=user, test=test, used=False).order_by('-id').first()

        if not state:
            return Response(
                {"detail": "No state found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )

        state.info = request.data["info"]
        state.initial_minutes = initial_minutes
        state.initial_seconds = initial_seconds
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
        data = request.data.get("data")  # Nội dung comment
        test_id = request.data.get("test_id")  # ID của bài kiểm tra
        parent_id = request.data.get("parent_id")  # ID của comment cha (nếu là reply)

        if not data:
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
        comment_data = {
            "user": user.id,
            "test": test.id,
            "parent": parent.id if parent else None,
            "content": data,
        }
        serializer = TestCommentSerializer(data=comment_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        comments = TestComment.objects.filter(test=test).order_by("-publish_date")

        # Serialize dữ liệu
        serializer = TestCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Lấy state mới nhất
        state = State.objects.filter(user=user, used=False).order_by('-id').first()

        if not state:
            return Response(
                {"detail": "No state found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize state
        serializer = StateSerializer(state)
        return Response(serializer.data, status=status.HTTP_200_OK)
