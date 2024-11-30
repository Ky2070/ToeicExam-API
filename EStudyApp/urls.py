from django.urls import path
from EStudyApp.views import DetailSubmitTestView, TestDetailView, TestListView, TestPartDetailView, CourseListView, \
    SubmitTestView, \
    QuestionSkillAPIView, DetailHistoryView, PartListView

urlpatterns = [
    # API lấy chi tiết test và part
    path('tests/', TestListView.as_view(), name='test-list'),  # API lấy danh sách tất cả các bài kiểm tra

    path('tests/<int:pk>/', TestDetailView.as_view(), name='test-detail'),  # API lấy thông tin chi tiết của một bài
    # kiểm tra
    path('tests/<int:test_id>/parts/', PartListView.as_view(), name='part-list'),

    path('tests-parts/<int:test_id>/', TestPartDetailView.as_view(), name='test-part-detail'),


    # API lấy skill và tính toán kết quả cho các câu hỏi
    path('submit/', SubmitTestView.as_view(), name='test-submit'),
    path('submit/history/', DetailSubmitTestView.as_view(), name='get-submit-id'),
    path('submit/result/<int:history_id>/', DetailHistoryView.as_view(), name='history-detail'),
    path('questions/<int:question_id>/skill/', QuestionSkillAPIView.as_view(), name='question-skill'),



    path('courses/', CourseListView.as_view(), name='course-list'),
]
