from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from Authentication.permissions import IsTeacher
from EStudyApp.services.history_service import HistoryService


@api_view(["GET"])
def get_latest_results(request):
    """
    API trả về 3 kết quả thi gần nhất của sinh viên chỉ định.
    Query params:
        student: id hoặc username của sinh viên (bắt buộc)
        limit: số kết quả muốn lấy (mặc định = 3)
    """
    # Tự check quyền thủ công
    if not IsTeacher().has_permission(request, get_latest_results):
        return Response(
            {"error": "Bạn không có quyền truy cập thông tin này (chỉ dành cho giáo viên)."},
            status=status.HTTP_403_FORBIDDEN
        )

    student_identifier = request.query_params.get("student")
    limit = request.query_params.get("limit", 3)

    # Kiểm tra input
    if not student_identifier:
        return Response(
            {"error": "Thiếu tham số 'student'"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        limit = int(limit)
    except ValueError:
        return Response(
            {"error": "limit phải là số nguyên"},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = HistoryService()
    results = service.get_latest_results(student_identifier, limit)

    return Response(results, status=status.HTTP_200_OK)
