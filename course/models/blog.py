from django.db import models
from Authentication.models import User


class Blog(models.Model):
    title = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    content = models.TextField()
    author = models.ForeignKey(User,
                               related_name='blog_user',
                               on_delete=models.DO_NOTHING)
    publish_date = models.DateTimeField(blank=True, null=True)


class CommentBlog(models.Model):
    user = models.ForeignKey(User,
                             related_name='commentblog_user',
                             on_delete=models.DO_NOTHING)
    blog = models.ForeignKey(Blog,
                             related_name='commentblog_blog',
                             on_delete=models.DO_NOTHING)
    parent = models.ForeignKey('self',
                               related_name='replies',
                               on_delete=models.DO_NOTHING,
                               blank=True,
                               null=True
                               )
    content = models.TextField()
    publish_date = models.DateTimeField(
        auto_now_add=True)  # Thời gian bình luận được tạo
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True
    )  # Thời gian bình luận được cập nhật
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True
    )  # Thời gian bình luận được tạo

    def __str__(self):
        return f'Comment by {self.user} on {self.blog}'
