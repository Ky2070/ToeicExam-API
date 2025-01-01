from django.urls import path
from course.views.api.course import course_list, create_course, course_detail
from course.views.api.lesson import lesson_list, lesson_detail, review_list_by_lesson
from course.views.api.blog import (
    blog_list, 
    blog_detail, 
    create_blog, 
    edit_blog,
    panel_blog_list,
    panel_blog_detail,
    BlogCreateView,
    BlogUpdateView,
    BlogDeleteView
)

urlpatterns = [
    path('create-course/', create_course, name='create-course'),
    path('course-list/', course_list, name='course-list'),
    path('course-list/<int:id>/', course_detail, name='course-detail'),

    # Lesson list and lesson-detail
    path('<int:course_id>/lessons/', lesson_list, name='lesson_list'),
    path('lessons/<int:id>/', lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/reviews/', review_list_by_lesson, name='review_list_by_lesson'),

    # Blog
    path('blogs/', blog_list, name='blog_list'),
    path('blogs/<int:id>/', blog_detail, name='blog_detail'),
    path('blogs/create/', create_blog, name='create_blog'),
    path('blogs/<int:id>/edit/', edit_blog, name='edit_blog'),

    # Panel
    path('panel/blogs/', panel_blog_list, name='panel_blog_list'),
    path('panel/blogs/create/', BlogCreateView.as_view(), name='panel_blog_create'),
    path('panel/blogs/<int:id>/update/', BlogUpdateView.as_view(), name='panel_blog_update'),
    path('panel/blogs/<int:id>/delete/', BlogDeleteView.as_view(), name='panel_blog_delete'),
    path('panel/blogs/<int:id>/', panel_blog_detail, name='panel_blog_detail'),
]
