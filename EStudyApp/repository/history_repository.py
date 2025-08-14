from django.core.exceptions import ObjectDoesNotExist
from EStudyApp.models import History, User

class HistoryRepository:

    def get_latest_results_by_student(self, student_identifier, limit=3):
        """
        Lấy kết quả 3 bài thi gần nhất của sinh viên chỉ định.
        student_identifier: có thể là user_id (int) hoặc username (str)
        """
        try:
            # Xác định student dựa vào ID hoặc username
            if isinstance(student_identifier, int) or str(student_identifier).isdigit():
                student = User.objects.get(id=int(student_identifier))
            else:
                student = User.objects.get(username=student_identifier)

        except ObjectDoesNotExist:
            return History.objects.none()  # Không tìm thấy thì trả về queryset rỗng

        # Lấy lịch sử thi
        return (
            History.objects
            .filter(user=student)
            .select_related("test")  # tránh query thừa
            .order_by("-end_time")[:limit]
        )
