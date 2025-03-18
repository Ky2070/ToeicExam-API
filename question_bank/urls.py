from django.urls import path
from .views import (
    QuestionBankListView,
    QuestionSetBankCreateView,
    QuestionSetBankDeleteView,
    QuestionSetBankDetailView,
    QuestionSetBankUpdateView,
    QuestionSetBankListView
)

urlpatterns = [
    path('', QuestionBankListView.as_view(), name='question-bank-list'),
    path('create/', QuestionSetBankCreateView.as_view(), name='question-set-bank-create'),
    path('question-sets/', QuestionSetBankListView.as_view(), name='question-set-bank-list'),
    path('<int:pk>/', QuestionSetBankDetailView.as_view(), name='question-set-bank-detail'),
    path('<int:pk>/update/', QuestionSetBankUpdateView.as_view(), name='question-set-bank-update'),
    # delete question set
    path('question-sets/<int:pk>/delete/', QuestionSetBankDeleteView.as_view(), name='question-set-bank-delete'),
]
