from django.db import models
from course.models.course import Course
from Authentication.models import User
from ckeditor.fields import RichTextField
from course.models.base import BaseModel

class Lesson(BaseModel):
    objects = None
    course = models.ForeignKey(Course,
                               related_name='lesson_course',
                               on_delete=models.CASCADE,
                               null=True
                               )
    title = models.TextField(
        blank=True,
        null=True
    )
    video = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    content = RichTextField(
        blank=True,
        null=True
    )
    quiz = models.TextField()


class ReviewLesson(BaseModel):
    objects = None
    user = models.ForeignKey(
        User,
        related_name='reviewlesson_user',
        on_delete=models.CASCADE,
        null=True
    )  # Người dùng bình luận
    lesson = models.ForeignKey(
        Lesson,
        related_name='reviewlesson_lesson',
        on_delete=models.CASCADE,
        null=True
    )  # Liên kết đến bài học (Lesson)
    content = models.TextField()  # Nội dung bình luận
    publish_date = models.DateTimeField(
        auto_now_add=True)  # Thời gian bình luận được tạo

    def __str__(self):
        return f'Comment by {self.user} on {self.lesson}'
