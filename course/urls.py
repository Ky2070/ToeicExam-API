from django.urls import path
from course.views.api.course import course_list, create_course, course_detail

urlpatterns = [
    path('create-course/', create_course, name='create-course'),
    path('course-list/', course_list, name='course-list'),
    path('course-list/<int:id>/', course_detail, name='course-detail'),
]
