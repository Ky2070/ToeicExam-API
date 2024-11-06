from django.urls import path
from .views import TestDetailView, TestListView

urlpatterns = [
    path('tests/', TestListView.as_view(), name='test-list'),  # API lấy danh sách tất cả các bài kiểm tra
    path('tests/<int:pk>/', TestDetailView.as_view(), name='test-detail'),  # API lấy thông tin chi tiết của một bài kiểm tra
]
