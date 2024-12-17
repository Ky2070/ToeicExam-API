from django.db import models
from course.models.course import Course
from Authentication.models import User

class Lesson(models.Model):
    course = models.ForeignKey(Course,
                               related_name='lesson_course',
                               on_delete=models.DO_NOTHING)
    title = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    content = models.TextField()
    quiz = models.TextField()
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True
    )  # Thời gian bình luận được cập nhật
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True
    )  # Thời gian bình luận được tạo


class ReviewLesson(models.Model):
    user = models.ForeignKey(
        User,
        related_name='reviewlesson_user',
        on_delete=models.DO_NOTHING
    )  # Người dùng bình luận
    lesson = models.ForeignKey(
        Lesson,
        related_name='reviewlesson_lesson',
        on_delete=models.DO_NOTHING
    )  # Liên kết đến bài học (Lesson)
    content = models.TextField()  # Nội dung bình luận
    publish_date = models.DateTimeField(
        auto_now_add=True)  # Thời gian bình luận được tạo
    updated_at = models.DateTimeField(
        auto_now=True)  # Thời gian bình luận được cập nhật
    created_at = models.DateTimeField(
        auto_now_add=True)  # Thời gian bình luận được tạo

    def __str__(self):
        return f'Comment by {self.user} on {self.lesson}'