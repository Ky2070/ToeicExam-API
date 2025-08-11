# from chat_bot.repositories.history_repository import HistoryRepository
#
# class HistoryService:
#     def __init__(self):
#         self.repo = HistoryRepository()
#
#     def get_latest_results(self, user_id, limit=3):
#         histories = self.repo.get_latest_results_by_user(user_id, limit)
#         return [
#             {
#                 "test_name": h.test.name if hasattr(h, 'test') else None,
#                 "score": h.score,
#                 "date": h.end_time.strftime("%Y-%m-%d %H:%M") if h.end_time else None
#             }
#             for h in histories
#         ]