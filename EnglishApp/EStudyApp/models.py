from django.db import models
from enum import Enum
from django.utils import timezone
from datetime import datetime, timedelta


# Create your models here.


class Test(models.Model):
    TYPE_TEST_CHOICES = [
        ('READING', 'Reading'),
        ('LISTENING', 'Listening'),
    ]
    
    test_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    type_test = models.CharField(
        max_length=30,
        choices=TYPE_TEST_CHOICES,
        null=True,
        blank=True
    )
    # Trường DateTimeField để lưu ngày và giờ làm bài kiểm tra
    test_date = models.DateTimeField(
        default=datetime.now,  # Giá trị mặc định là thời gian hiện tại
        blank=True,
        null=True
    )

    # Thời gian làm bài kiểm tra (ví dụ: 120 phút)
    duration = models.DurationField(
        default=timedelta(minutes=120),  # Thời gian làm bài mặc định là 120 phút
        blank=True,
        null=True
    )

    def __str__(self):
        return self.test_name


class Question(models.Model):
    DIFFICULTY_LEVEL_CHOICES = [
        ('BASIC', 'Basic'),
        ('MEDIUM', 'Medium'),
        ('DIFFICULTY', 'Difficulty'),
        ('VERY_DIFFICULTY', 'Very Difficulty')
    ]
    CORRECT_ANSWER_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D")
    ]
    question_text = models.TextField()
    difficulty_level = models.CharField(
        max_length=30,
        choices=DIFFICULTY_LEVEL_CHOICES,
        default=('BASIC', 'Basic'),
    )
    correct_answer = models.CharField(
        max_length=10,
        choices=CORRECT_ANSWER_CHOICES,
        default='',
        blank=True,
        null=True
    )
    question_number = models.IntegerField(
        null=True,
        blank=True
    )
    answers = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        """Soft delete: cập nhật ngày xóa thay vì xóa hẳn trong DB"""
        self.deleted_at = timezone.now()
        self.save()

    def delete(self, *args, **kwargs):
        """Override delete để thực hiện soft delete"""
        self.soft_delete()

    def __str__(self):
        return self.question_text


class QuestionType(models.Model):
    type_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    count = models.IntegerField(
        blank=True,
        null=True
    )
    # duration = models.TimeField(
    #     default=time(0, 10, 0),  # Giá trị mặc định là 30 phút
    #     blank=True,  # Cho phép trường này để trống trong form
    #     null=True,  # Cho phép lưu giá trị NULL trong cơ sở dữ liệu
    #     help_text="Thời gian giới hạn cho câu hỏi (giờ:phút:giây)"
    # )
    description = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.type_name


class Part(models.Model):
    SKILL_CHOICES = [
        ('READING', 'Reading'),
        ('LISTENING', 'Listening'),
    ]
    part_name = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    description = models.TextField(
        blank=True,  # Cho phép trường này để trống
        null=True  # Cho phép lưu giá trị NULL
    )
    skill = models.CharField(
        max_length=20,
        choices=SKILL_CHOICES,
        default='',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.part_name


class QuestionSet(models.Model):
    audio = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    page = models.TextField(
        blank=True,  # Cho phép trường này để trống
        null=True  # Cho phép lưu giá trị NULL
    )
    image = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.page
