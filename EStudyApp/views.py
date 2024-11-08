from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Test, Part, Course
from .serializers import TestDetailSerializer, TestSerializer, PartSerializer, CourseSerializer


class TestDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            # Nạp đầy đủ các phần, bộ câu hỏi và câu hỏi liên quan đến bài kiểm tra
            test = Test.objects.prefetch_related(
                'part_test',
            ).get(pk=pk)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # Sử dụng serializer mới để nạp dữ liệu liên kết
        serializer = TestDetailSerializer(test)
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


class TestPartDetailView(APIView):
    def get(self, request, test_id, part_id, format=None):
        try:
            # Tìm kiếm bài kiểm tra dựa trên `test_id`
            test = Test.objects.prefetch_related('part_test').get(pk=test_id)
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

        return Response({
            "test": test_serializer.data,
            "part": part_serializer.data
        }, status=status.HTTP_200_OK)
    
class CourseListView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many = True)
        return Response(serializer.data)
    
# class CourseDetailView(APIView):
    # def get(self, request, id):

