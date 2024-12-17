from django.db import models
from django.utils import timezone
from Authentication.models import User
from ckeditor.fields import RichTextField
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Course(models.Model):
    objects = None
    user = models.ForeignKey(User,
                             related_name='course_user',
                             on_delete=models.DO_NOTHING)
    title = models.TextField(
        blank=True,
        null=True
    )
    description = RichTextField(
        blank=True,
        null=True
    )
    COURSE_LEVEL_CHOICES = [
        ('BASIC', 'Basic'),
        ('ADVANCED', 'Advanced'),
        ('PRO', 'Pro')
    ]
    level = models.CharField(
        max_length=30,
        choices=COURSE_LEVEL_CHOICES,
        default=('BASIC', 'Basic'),
    )
    banner = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    # thông tin khóa học text array
    info = ArrayField(
        models.TextField(blank=True, null=True),
        blank=True,
        null=True
    )
    
    # mục tiêu khóa học text array
    target = ArrayField(
        models.TextField(blank=True, null=True),
        blank=True,
        null=True
    )
    
    duration = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.title
    
    @property
    def video_id(self):
        """Extract YouTube video ID from URL"""
        if self.video_url:
            if 'youtube.com/watch?v=' in self.video_url:
                return self.video_url.split('watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in self.video_url:
                return self.video_url.split('youtu.be/')[1]
        return None
    



