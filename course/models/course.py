from django.db import models
from django.utils import timezone
from Authentication.models import User

# Create your models here.
class Course(models.Model):
    objects = None
    user = models.ForeignKey(User,
                             related_name='course_user',
                             on_delete=models.DO_NOTHING)
    title = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=100,
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
    duration = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    


