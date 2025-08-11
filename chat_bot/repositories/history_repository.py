# from EStudyApp.models import History, HistoryTraining
#
# class HistoryRepository:
#     def get_latest_results_by_user(self, user_id, limit=3):
#         """
#         Lấy kết quả thi mới nhất của sinh viên.
#         """
#         return (
#             History.objects
#             .filter(user_id=user_id)
#             .order_by('-end_time')[:limit]
#         )