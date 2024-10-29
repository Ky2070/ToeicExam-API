from django.db import models
from enum import Enum
from django.utils import timezone
from datetime import datetime, timedelta

from Authentication.models import User # type: ignore


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
        # Thời gian làm bài mặc định là 120 phút
        default=timedelta(minutes=120),
        blank=True,
        null=True
    )

    def __str__(self):
        return self.test_name


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


# class Part(models.Model):
#     SKILL_CHOICES = [
#         ('READING', 'Reading'),
#         ('LISTENING', 'Listening'),
#     ]
#     part_name = models.CharField(
#         max_length=20,
#         null=True,
#         blank=True
#     )
#     description = models.TextField(
#         blank=True,  # Cho phép trường này để trống
#         null=True  # Cho phép lưu giá trị NULL
#     )
#     skill = models.CharField(
#         max_length=20,
#         choices=SKILL_CHOICES,
#         default='',
#         blank=True,
#         null=True
#     )

#     def __str__(self):
#         return self.part_name

class PartDescription(models.Model):
    part_name = models.CharField(max_length=10)
    part_description = models.TextField(null=True, blank=True)

    SKILL_CHOICES = [
        ('READING', 'Reading'),
        ('LISTENING', 'Listening'),
    ]

    skill = models.CharField(
        max_length=30,
        choices=SKILL_CHOICES,
        null=True,
        blank=True
    )

    QUESTION_QUANTITY_CHOICES = [
        (6, 'PART_1'),
        (25, 'PART_2'),
        (39, 'PART_3'),
        (30, 'PART_4'),
        (30, 'PART_5'),
        (16, 'PART_6'),
        (54, 'PART_7'),
    ]

    quantity = models.IntegerField(
        null=True, blank=True, choices=QUESTION_QUANTITY_CHOICES)

    def __str__(self):
        return self.part_name


class Part(models.Model):
    part_description = models.ForeignKey(
        PartDescription, related_name='part_part_description', on_delete=models.DO_NOTHING)
    test = models.ForeignKey(Test, related_name='part_test', on_delete=models.DO_NOTHING)
    pass


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


class Question(models.Model):
    question_set = models.ForeignKey(QuestionSet, related_name='question_question_set', on_delete=models.DO_NOTHING)

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


class PartQuestionSet(models.Model):
    part = models.ForeignKey(Part, related_name='partquestionset_part', on_delete=models.DO_NOTHING)
    question_set = models.ForeignKey(QuestionSet, related_name='partquestionset_question_set', on_delete=models.DO_NOTHING)


class History(models.Model):
    user = models.ForeignKey(User, related_name='history_user', on_delete=models.DO_NOTHING)
    test = models.ForeignKey(Test, related_name='history_test', on_delete=models.DO_NOTHING)
    score = models.DecimalField(
        max_digits=3, decimal_places=0, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    correct_answers = models.IntegerField(blank=True, null=True)
    wrong_answers = models.IntegerField(blank=True, null=True)
    unanswer_questions = models.IntegerField(blank=True, null=True)
    percentage_score = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True)
    listening_score = models.DecimalField(
        max_digits=3, decimal_places=0, blank=True, null=True)
    reading_score = models.DecimalField(
        max_digits=3, decimal_places=0, blank=True, null=True)
    complete = models.BooleanField(default=False)
    test_result = models.JSONField(blank=True, null=True)
