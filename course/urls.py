from django.urls import path
from course.views.api.course import create_course

urlpatterns = [
    path('create-course/', create_course, name='create-course'),
]
