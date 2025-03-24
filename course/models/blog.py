from django.db import models
from Authentication.models import User
from EStudyApp.models import QuestionSet
from course.models.base import BaseModel

class Blog(BaseModel):
    title = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    content = models.TextField()
    part_info = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    from_ques = models.IntegerField(
        blank=True,
        null=True
    )
    to_ques = models.IntegerField(
        blank=True,
        null=True
    )
    author = models.ForeignKey(User,
                               related_name='blog_user',
                               on_delete=models.CASCADE,
                               null=True
                               )
    questions_set = models.ForeignKey(QuestionSet,
                                     related_name='blog_questions_set',
                                     on_delete=models.CASCADE,
                                     blank=True,
                                     null=True)
    is_published = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('DELETED', 'Deleted')
    ]
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    @property
    def likes_count(self):
        return self.blog_likes.count()


class CommentBlog(BaseModel):
    user = models.ForeignKey(User,
                             related_name='commentblog_user',
                             on_delete=models.CASCADE,
                             null=True
                             )
    blog = models.ForeignKey(Blog,
                             related_name='commentblog_blog',
                             on_delete=models.CASCADE,
                             null=True
                             )
    parent = models.ForeignKey('self',
                               related_name='replies',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    content = models.TextField()
    publish_date = models.DateTimeField(
        auto_now_add=True)  # Thời gian bình luận được tạo


    def __str__(self):
        return f'Comment by {self.user} on {self.blog}'
