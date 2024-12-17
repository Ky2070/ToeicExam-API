from django.urls import path
from course.views.api.course import course_list, create_course, course_detail
from course.views.api.lesson import lesson_list, lesson_detail, review_list_by_lesson

urlpatterns = [
    path('create-course/', create_course, name='create-course'),
    path('course-list/', course_list, name='course-list'),
    path('course-list/<int:id>/', course_detail, name='course-detail'),

    # Lesson list and lesson-detail

    path('lessons/', lesson_list, name='lesson_list'),
    path('lessons/<int:id>/', lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/reviews/', review_list_by_lesson, name='review_list_by_lesson'),
    
]
