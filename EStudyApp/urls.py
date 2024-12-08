from django.urls import path
from EStudyApp.views import DetailSubmitTestView, TestDetailView, TestListView, TestPartDetailView, CourseListView, \
    SubmitTestView, \
    QuestionSkillAPIView, DetailHistoryView, PartListView, QuestionListView, StateCreateView, StateView, \
    TestCommentView, CommentView, SubmitTrainingView, SearchTestsAPIView

urlpatterns = [
    # API lấy chi tiết test và part
    path('tests/', TestListView.as_view(), name='test-list'),  # API lấy danh sách tất cả các bài kiểm tra

    path('tests/search-tests/', SearchTestsAPIView.as_view(), name='search_tests_api'),

    path('tests/<int:pk>/', TestDetailView.as_view(), name='test-detail'),  # API lấy thông tin chi tiết của một bài
    # kiểm tra
    path('tests/<int:test_id>/parts/', PartListView.as_view(), name='part-list'),

    path('tests-parts/<int:test_id>/', TestPartDetailView.as_view(), name='test-part-detail'),
    path('tests/<int:test_id>/comments/', CommentView.as_view(), name='test-comments'),
    path('questions/', QuestionListView.as_view(), name='question-list'),

    # API lấy skill và tính toán kết quả cho các câu hỏi
    path('submit/', SubmitTestView.as_view(), name='test-submit'),
    path('submit/history/', DetailSubmitTestView.as_view(), name='get-submit-id'),
    path('submit/result/<int:history_id>/', DetailHistoryView.as_view(), name='history-detail'),
    path('questions/<int:question_id>/skill/', QuestionSkillAPIView.as_view(), name='question-skill'),

    path('submit/training/', SubmitTrainingView.as_view(), name='training-submit'),
    # Lưu state
    path('create/state/', StateCreateView.as_view(), name='state-create'),

    path('state/', StateView.as_view(), name='state'),

    path('create/comments/', TestCommentView.as_view(), name='create-comments'),
    path('edit/comments/<int:pk>/', TestCommentView.as_view(), name='comment-update'),
    path('delete/comments/<int:pk>/', TestCommentView.as_view(), name='comment-delete'),

    path('courses/', CourseListView.as_view(), name='course-list'),
]
