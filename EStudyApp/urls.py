from django.urls import path
from EStudyApp.views import DetailSubmitTestView, DetailTrainingView, PartListQuestionsSetAPIView, TestDetailView, TestListView, TestPartDetailView, \
    SubmitTestView, \
    QuestionSkillAPIView, DetailHistoryView, PartListView, QuestionListView, StateCreateView, StateView, \
    TestCommentView, CommentView, SubmitTrainingView, SearchTestsAPIView, TestCreateAPIView, TestUpdateAPIView, \
    TestDeleteAPIView, GetPartAPIView, CreatePartAPIView, UpdatePartAPIView, ListTestView, DeletePartAPIView, \
    CreateQuestionAPIView, DetailQuestionAPIView, UpdateQuestionAPIView, DeleteQuestionAPIView, TagListView, \
    # TestByTagView

urlpatterns = [
    # Tag for Test-list
    # path('tags/', TagListView.as_view(), name='tag-list'),
    # path('tags/<int:tag_id>/tests/', TestByTagView.as_view(), name='test-by-tag'),
    # API lấy chi tiết test và part
    path('tests/', TestListView.as_view(), name='test-list'),  # API lấy danh sách tất cả các bài kiểm tra

    path('tests/create/', TestCreateAPIView.as_view(), name='test-create'),
    path('tests/test-list/', ListTestView.as_view(), name='list-test'),
    path('tests/test-list/<int:id>/', TestCreateAPIView.as_view(), name='test-detail'),

    path('tests/<int:id>/update/', TestUpdateAPIView.as_view(), name='test-update'),  # Sửa bài thi
    path('tests/<int:id>/delete/', TestDeleteAPIView.as_view(), name='test-delete'),  # Xóa bài thi

    path('tests/search-tests/', SearchTestsAPIView.as_view(), name='search_tests_api'),

    path('tests/<int:pk>/', TestDetailView.as_view(), name='test-detail'),  # API lấy thông tin chi tiết của một bài
    # kiểm tra
    path('tests/<int:test_id>/parts/', PartListView.as_view(), name='part-list'),

    path('tests-parts/<int:test_id>/', TestPartDetailView.as_view(), name='test-part-detail'),
    path('tests/<int:test_id>/comments/', CommentView.as_view(), name='test-comments'),
    # Part API

    path('parts/', GetPartAPIView.as_view(), name='part-list'),  # GET all
    path('parts/<int:id>/', GetPartAPIView.as_view(), name='part-detail'),  # GET theo ID
    path('parts/create/<int:test_id>/', CreatePartAPIView.as_view(), name='part-create'),  # POST
    path('parts/update/<int:id>/', UpdatePartAPIView.as_view(), name='part-update'),  # PUT
    path('parts/delete/<int:id>/', DeletePartAPIView.as_view(), name='part-delete'),  # API xóa phần (DELETE)
    path('parts/<int:part_id>/questions_set/', PartListQuestionsSetAPIView.as_view(), name='part-api'),  # GET theo ID

    # Question API

    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('questions/create/', CreateQuestionAPIView.as_view(), name='question-create'),  # Tạo câu hỏi mới
    path('questions/<int:id>/', DetailQuestionAPIView.as_view(), name='question-detail'),  # Chi tiết câu hỏi
    path('questions/update/<int:id>/', UpdateQuestionAPIView.as_view(), name='question-update'),  # Cập nhật câu hỏi
    path('questions/delete/<int:id>/', DeleteQuestionAPIView.as_view(), name='question-delete'),  # Xóa câu hỏi
    
    # API lấy skill và tính toán kết quả cho các câu hỏi
    path('submit/', SubmitTestView.as_view(), name='test-submit'),
    path('submit/history/', DetailSubmitTestView.as_view(), name='get-submit-id'),
    path('submit/result/<int:history_id>/', DetailHistoryView.as_view(), name='history-detail'),
    path('questions/<int:question_id>/skill/', QuestionSkillAPIView.as_view(), name='question-skill'),

    path('submit/training/', SubmitTrainingView.as_view(), name='training-submit'),
    path('submit/training/<int:history_id>/', DetailTrainingView.as_view(), name='training-detail'),
    # Lưu state
    path('create/state/', StateCreateView.as_view(), name='state-create'),

    path('state/', StateView.as_view(), name='state'),

    path('create/comments/', TestCommentView.as_view(), name='create-comments'),
    path('edit/comments/<int:pk>/', TestCommentView.as_view(), name='comment-update'),
    path('delete/comments/<int:pk>/', TestCommentView.as_view(), name='comment-delete'),

    # path('courses/', CourseListView.as_view(), name='course-list'),
]
