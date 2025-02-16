from django.urls import path
from .views import classify_question

urlpatterns = [
    path('classify/', classify_question, name='classify_question'),
]
