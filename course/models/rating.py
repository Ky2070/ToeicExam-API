from django.db import models
from EStudyApp.base_model import BaseModel
from Authentication.models import User
from course.models.course import Course


class Rating(BaseModel):
    user = models.ForeignKey(
        User,
        related_name='user_rating',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    course = models.ForeignKey(
        Course,
        related_name='course_rating',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    star = models.IntegerField(
        blank=True,
        null=True,
    )

    class Meta:
        # Each user can rate a course only once
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} rated {self.course.title}: {self.rating}"
