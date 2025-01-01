from django.urls import path
from course.views.api.course import CourseListView, create_course, course_detail
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
from course.views.api.review import (
    get_lesson_reviews, 
    create_review, 
    manage_review,
    reply_to_review
)
from course.views.api.comment import (
    get_blog_comments,
    create_comment,
    reply_to_comment,
    manage_comment
)
from course.views.api.rating import rate_course
from course.views.api.like import toggle_like_blog, get_blog_likes, check_user_like

urlpatterns = [
    path('create-course/', create_course, name='create-course'),
    path('course-list/', CourseListView.as_view(), name='course-list'),
    path('course-list/<int:id>/', course_detail, name='course-detail'),

    # Lesson list and lesson-detail
    path('<int:course_id>/lessons/', lesson_list, name='lesson_list'),
    path('lessons/<int:id>/', lesson_detail, name='lesson_detail'),
    # path('lessons/<int:lesson_id>/reviews/', review_list_by_lesson, name='review_list_by_lesson'),
    path('lessons/<int:lesson_id>/reviews/', get_lesson_reviews, name='lesson-reviews'),
    path('lessons/<int:lesson_id>/reviews/create/', create_review, name='create-review'),
    path('reviews/<int:review_id>/reply/', reply_to_review, name='reply-to-review'),
    path('reviews/<int:review_id>/', manage_review, name='manage-review'),

    # Blog
    path('blogs-list/', blog_list, name='blog_list'),
    path('blogs/<int:id>/', blog_detail, name='blog_detail'),
    path('blogs/create/', create_blog, name='create_blog'),
    path('blogs/<int:id>/edit/', edit_blog, name='edit_blog'),

    # Panel
    path('panel/blogs/', panel_blog_list, name='panel_blog_list'),
    path('panel/blogs/create/', BlogCreateView.as_view(), name='panel_blog_create'),
    path('panel/blogs/<int:id>/update/', BlogUpdateView.as_view(), name='panel_blog_update'),
    path('panel/blogs/<int:id>/delete/', BlogDeleteView.as_view(), name='panel_blog_delete'),
    path('panel/blogs/<int:id>/', panel_blog_detail, name='panel_blog_detail'),

    # Blog Comments
    path('blogs/<int:blog_id>/comments/', get_blog_comments, name='blog-comments'),
    path('blogs/<int:blog_id>/comments/create/', create_comment, name='create-comment'),
    path('comments/<int:comment_id>/reply/', reply_to_comment, name='reply-to-comment'),
    path('comments/<int:comment_id>/', manage_comment, name='manage-comment'),
    
    # Rating
    path('rate/course/<int:course_id>/', rate_course, name='rate-course'),

    # Blog Likes
    path('blogs/<int:blog_id>/toggle-like/', toggle_like_blog, name='toggle-blog-like'),
    path('blogs/<int:blog_id>/likes/', get_blog_likes, name='blog-likes'),
    path('blogs/<int:blog_id>/check-like/', check_user_like, name='check-blog-like'),
]
