from django.db import models
from EStudyApp.base_model import BaseModel
from Authentication.models import User
from course.models.blog import Blog


class LikeBlog(BaseModel):
    user = models.ForeignKey(
        User, 
        related_name='user_likes',
        on_delete=models.CASCADE
    )
    blog = models.ForeignKey(
        Blog, 
        related_name='blog_likes',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'blog')  # Each user can like a blog only once

    def __str__(self):
        return f"{self.user.username} likes {self.blog.title}"
    