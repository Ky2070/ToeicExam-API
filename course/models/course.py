from django.db import models
from django.utils import timezone
from Authentication.models import User
from ckeditor.fields import RichTextField
from django.contrib.postgres.fields import ArrayField
from course.models.base import BaseModel

# Create your models here.
class Course(BaseModel):
    objects = None
    user = models.ForeignKey(User,
                             related_name='course_user',
                             on_delete=models.CASCADE,
                             null=True
                             )
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

    cover = models.CharField(
        max_length=255,
        blank=True,
        null=True
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

    def __str__(self):
        return self.title
