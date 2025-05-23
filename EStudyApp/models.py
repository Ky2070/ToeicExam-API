from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import copy
import random
from ckeditor.fields import RichTextField
from datetime import datetime, timedelta
from django.utils import timezone

from Authentication.models import User  # type: ignore
from EStudyApp.base_model import BaseModel


# Create your models here.

class Tag(BaseModel):
    DoesNotExist = None
    objects = None
    name = models.CharField(
        unique=True,
        max_length=125,
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=125,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Test(BaseModel):
    DoesNotExist = None
    objects = None
    TYPE_TEST_CHOICES = [
        ('Online', 'Online'),
        ('Practice', 'Practice'),
        ('All', 'All')
    ]

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    types = models.CharField(
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
    # Số câu hỏi (mặc định 200)
    question_count = models.IntegerField(
        default=200
    )

    # Số phần thi (mặc định 7)
    part_count = models.IntegerField(
        default=7
    )
    
    tags = models.ManyToManyField(Tag, related_name='tests', blank=True)
    publish = models.BooleanField(default=False)
    
    publish_date = models.DateTimeField(
        # default=datetime.now,
        blank=True,
        null=True
    )
    
    close_date = models.DateTimeField(
        # default=datetime.now,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
    
    @property
    def part_total(self):
        return Part.objects.filter(test=self).count()
    
    @property
    def question_total(self):
        question_total = Question.objects.filter(test=self).count()
        return question_total
        
    def update_publish_status(self):
        """
        Update the publish status based on publish_date and close_date.
        Returns True if the status was changed, False otherwise.
        """
        current_time = timezone.now()
        
        # Check if we need to publish this test
        if (not self.publish and 
            self.publish_date and self.publish_date <= current_time and
            (not self.close_date or self.close_date > current_time)):
            self.publish = True
            self.save(update_fields=['publish'])
            return True
            
        # Check if we need to unpublish this test
        elif (self.publish and 
              self.close_date and self.close_date <= current_time):
            self.publish = False
            self.save(update_fields=['publish'])
            return True
            
        return False


# class UserTestResult(models.Model):
#     user = models.ForeignKey(User,
#                              related_name='usertestresult_user',
#                              on_delete=models.CASCADE)
#     test = models.ForeignKey(Test,
#                              related_name='usertestresult_test',
#                              on_delete=models.CASCADE)
#     test_date = models.DateTimeField()
#     time_taken = models.TimeField()


class QuestionType(BaseModel):
    objects = None
    name = models.CharField(
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
        return f'{self.name} - {self.description}'


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

class PartDescription(BaseModel):
    part_name = models.CharField(max_length=10)
    part_description = models.TextField(null=True, blank=True)
    part_number = models.IntegerField(null=True, blank=True)

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
    DoesNotExist = None
    objects = None
    part_description = models.ForeignKey(
        PartDescription, related_name='part_part_description', on_delete=models.CASCADE, null=True, blank=False)
    test = models.ForeignKey(
        Test, related_name='part_test', on_delete=models.CASCADE, null=True, blank=True)
    pass

    def __str__(self):
        return f'{self.part_description} - {self.test}'
    
    @property
    def part_number(self):
        return self.part_description.part_number


class QuestionSet(models.Model):
    objects = None
    test = models.ForeignKey(Test,
                             related_name='question_set_test',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True
                             )
    part = models.ForeignKey(Part,
                             related_name='question_set_part',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True
                             )
    audio = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    page = RichTextField(
        blank=True,  # Cho phép trường này để trống
        null=True  # Cho phép lưu giá trị NULL
    )

    image = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    from_ques = models.IntegerField(blank=True, null=True)
    to_ques = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.page:
            page_content = str(self.page)
            if len(page_content) > 50:
                return f'{page_content[:50]}...'
            return page_content
        return "No Page Content"


class Question(BaseModel):
    DoesNotExist = None
    objects = None
    test = models.ForeignKey(Test,
                             related_name='question_test',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True
                             )
    question_set = models.ForeignKey(QuestionSet,
                                     related_name='question_question_set',
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    question_type = models.ForeignKey(QuestionType,
                                      related_name='question_question_type',
                                      on_delete=models.CASCADE,
                                      null=True,
                                      blank=True)
    part = models.ForeignKey(Part,
                             related_name='question_part',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True
                             )
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
    question_text = models.TextField(null=True, blank=True)
    difficulty_level = models.CharField(
        max_length=30,
        choices=DIFFICULTY_LEVEL_CHOICES,
        default='',  # Sử dụng giá trị đầu tiên trong tuple
        blank=True,
        null=True

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

    def soft_delete(self):
        """Soft delete: cập nhật ngày xóa thay vì xóa hẳn trong DB"""
        self.deleted_at = timezone.now()
        self.save()

    def delete(self, *args, **kwargs):
        """Override delete để thực hiện soft delete"""
        self.soft_delete()

    def __str__(self):
        return f'{self.question_number} - {self.question_text}'

    @property
    def part_id(self):
        return self.part.id


class PartQuestionSet(BaseModel):
    part = models.ForeignKey(
        Part, related_name='partquestionset_part', on_delete=models.CASCADE, null=True)
    question_set = models.ForeignKey(
        QuestionSet, related_name='partquestionset_question_set', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.part} - {self.question_set}"


class History(BaseModel):
    objects = None
    user = models.ForeignKey(
        User, related_name='history_user', on_delete=models.CASCADE, null=True)
    test = models.ForeignKey(
        Test, related_name='history_test', on_delete=models.CASCADE, null=True)
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

    def __str__(self):
        return f"{self.user} - {self.test}"

    @property
    def completion_time(self):
        delta = self.end_time - self.start_time
        return round(delta.total_seconds())


class HistoryTraining(BaseModel):
    user = models.ForeignKey(
        User, related_name='training_user', on_delete=models.CASCADE, null=True)
    test = models.ForeignKey(
        Test, related_name='training_test', on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    correct_answers = models.IntegerField(blank=True, null=True)
    wrong_answers = models.IntegerField(blank=True, null=True)
    unanswer_questions = models.IntegerField(blank=True, null=True)
    percentage_score = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True)
    complete = models.BooleanField(default=False)
    test_result = models.JSONField(blank=True, null=True)
    part_list = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user} - {self.test}"

    @property
    def completion_time(self):
        delta = self.end_time - self.start_time
        return round(delta.total_seconds())


class TestComment(BaseModel):
    user = models.ForeignKey(
        User,
        related_name='testcomment_user',
        on_delete=models.CASCADE,
        null=True
    )  # Người dùng bình luận
    test = models.ForeignKey(
        Test,
        related_name='testcomment_test',
        on_delete=models.CASCADE,
        null=True
    )  # Liên kết đến bài học (Lesson)
    parent = models.ForeignKey(
        'self',
        related_name='replies',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )  # Khóa ngoại đệ quy để hỗ trợ trả lời bình luận
    content = models.TextField()  # Nội dung bình luận
    publish_date = models.DateTimeField(
        auto_now_add=True)  # Thời gian bình luận được tạo

    def __str__(self):
        return f'Comment by {self.user} on {self.test}'

    @property
    def replies(self):
        return TestComment.objects.filter(parent=self)

    @property
    def get_replies(self):
        return self.replies.all()


class Flashcard(BaseModel):
    user = models.ForeignKey(User,
                             related_name='flashcard_user',
                             on_delete=models.CASCADE,
                             null=True)
    term = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    definition = models.TextField()
    FLASHCARD_LEVEL_CHOICES = [
        ('BASIC', 'Basic'),
        ('MEDIUM', 'Medium'),
        ('DIFFICULTY', 'Difficulty')
    ]
    level = models.CharField(
        max_length=30,
        choices=FLASHCARD_LEVEL_CHOICES,
        default=('BASIC', 'Basic'),
    )
    example = models.TextField()


class State(BaseModel):
    user = models.ForeignKey(User,
                             related_name='state_user',
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    test = models.ForeignKey(Test, related_name='state_test',
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True
                             )
    time = models.DurationField(blank=True, null=True)
    initial_minutes = models.IntegerField(blank=True, null=True)
    initial_seconds = models.IntegerField(blank=True, null=True)
    time_taken = models.IntegerField(blank=True, null=True)
    time_start = models.DateTimeField(blank=True, null=True)

    name = models.CharField(
        max_length=125,
        blank=True,
        null=True
    )
    info = models.JSONField(
        blank=True,
        null=True
    )
    used = models.BooleanField(
        default=False
    )
