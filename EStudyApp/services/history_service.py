from EStudyApp.repository.history_repository import HistoryRepository

class HistoryService:
    def __init__(self):
        self.repo = HistoryRepository()

    def get_latest_results(self, student_identifier, limit=3):
        """
        Lấy danh sách kết quả thi gần nhất của sinh viên, format dữ liệu trả về.
        student_identifier: id hoặc username của sinh viên
        """
        histories = self.repo.get_latest_results_by_student(student_identifier, limit)

        # Format dữ liệu trả về
        results = []
        for h in histories:
            results.append({
                "student": h.user.username if h.user else None,
                "test_name": h.test.name if h.test else None,
                "score": float(h.score) if h.score is not None else None,
                "listening_score": float(h.listening_score) if h.listening_score is not None else None,
                "reading_score": float(h.reading_score) if h.reading_score is not None else None,
                "date": h.end_time.strftime("%Y-%m-%d %H:%M") if h.end_time else None
            })

        return results