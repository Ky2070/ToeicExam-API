# # chat_bot/controllers/history_controller.py
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from chat_bot.services.history_service import HistoryService
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_latest_results(request):
#     """
#     API trả về 3 kết quả thi gần nhất của sinh viên đang đăng nhập.
#     """
#     service = HistoryService()
#     data = service.get_latest_results(request.user.id, limit=3)
#     return Response(data)
