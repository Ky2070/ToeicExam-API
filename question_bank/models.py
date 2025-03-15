from datetime import timezone
from django.db import models
from ckeditor.fields import RichTextField
from EStudyApp.base_model import BaseModel
from EStudyApp.models import PartDescription, QuestionType

# Create your models here.


class QuestionSetBank(BaseModel):
    objects = None

    part_description = models.ForeignKey(
        PartDescription, related_name='part_description_question_set_bank', on_delete=models.CASCADE, null=True, blank=False)
    audio = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    page = RichTextField(
        blank=True,
        null=True
    )

    image = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    from_ques = models.IntegerField(blank=True, null=True)
    to_ques = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.page:
            page_content = str(self.page)
            if len(page_content) > 50:
                return f'{page_content[:50]}...'
            return page_content
        return "No Page Content"
    

class QuestionBank(BaseModel):
    DoesNotExist = None
    objects = None

    question_set = models.ForeignKey(QuestionSetBank,
                                     related_name='question_bank_question_set_bank',
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    question_type = models.ForeignKey(QuestionType,
                                      related_name='question_bank_question_type',
                                      on_delete=models.CASCADE,
                                      null=True,
                                      blank=True)
    part_description = models.ForeignKey(
        PartDescription, related_name='part_description_question_bank', on_delete=models.CASCADE, null=True, blank=False)
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
