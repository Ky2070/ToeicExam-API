from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Test
from .serializers import TestSerializer



class TestDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            # Nạp đầy đủ các phần, bộ câu hỏi và câu hỏi liên quan đến bài kiểm tra
            test = Test.objects.prefetch_related(
                'part_test',
                'part_test__question_set_part',
                'part_test__question_set_part__question_question_set'
            ).get(pk=pk)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # Sử dụng serializer mới để nạp dữ liệu liên kết
        serializer = TestSerializer(test)
        return Response(serializer.data)


# Bạn có thể viết một view tương tự để lấy danh sách tất cả các bài kiểm tra nếu cần:
class TestListView(APIView):
    """
    API view để lấy danh sách tất cả các bài kiểm tra.
    """

    def get(self, request, format=None):
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)
